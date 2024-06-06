import re
from opendevin.events.action.commands import CmdRunAction
from opendevin.events.action.editor import CreateFileAction, ReadFileAction, WriteFileAction
from opendevin.events.action.message import MessageAction
from opendevin.events.observation.commands import CmdOutputObservation
from opendevin.events.observation.editor import CreateFileObservation, ReadFileObservation, WriteFileObservation
from opendevin.llm.llm import LLM
from opendevin.controller.agent import Agent
from opendevin.controller.state.state import State
from opendevin.events.action import Action, AgentFinishAction
from opendevin.events.observation import Observation
from agenthub.codeact_agent.vscode_prompt import (
    SYSTEM_PREFIX,
    COMMAND_DOCS,
    SYSTEM_SUFFIX,
    EXAMPLES,
)

def parse_response(response) -> str:
    """
    Completes the response snippet to contain the full XML tags.
    """
    action = response.choices[0].message.content
    for lang in ['bash', 'editor']:
        if f'<execute_{lang}>' in action and f'</execute_{lang}>' not in action:
            action += f'</execute_{lang}>'

    return action


def action_to_str(action: Action) -> str:
    if isinstance(action, CmdRunAction):
        return f'{action.thought}\n<execute_bash>\n{action.command}\n</execute_bash>'
    elif isinstance(action, CreateFileAction) or isinstance(action, ReadFileAction):
        return f'{action.thought}\n<execute_editor>\n<operation>create</operation><filename>{action.path}</filename>\n</execute_editor>'
    elif isinstance(action, WriteFileAction):
        return f'{action.thought}\n<execute_editor>\n<operation>edit</operation><filename>{action.path}</filename><start>{action.start}</start><end>{action.stop}</end><content>{action.content}</content>\n</execute_editor>'
    elif isinstance(action, MessageAction):
        return action.content
    return ''


def truncate_observation(observation: str, max_chars: int = 10_000) -> str:
    """
    Truncate the middle of the observation if it is too long.
    """
    if len(observation) <= max_chars:
        return observation
    half = max_chars // 2
    return (
        observation[:half]
        + '\n[... Observation truncated due to length ...]\n'
        + observation[-half:]
    )



def get_action_message(action: Action) -> dict[str, str] | None:
    if (
        isinstance(action, CreateFileAction)
        or isinstance(action, ReadFileAction)
        or isinstance(action, WriteFileAction)
        or isinstance(action, CmdRunAction)
        or isinstance(action, MessageAction)
    ):
        return {
            'role': 'user' if action.source == 'user' else 'assistant',
            'content': action_to_str(action),
        }

    return None


def get_observation_message(obs) -> dict[str, str] | None:
    if isinstance(obs, CmdOutputObservation):
        content = 'OBSERVATION:\n' + truncate_observation(obs.content)
        content += (
            f'\n[Command {obs.command_id} finished with exit code {obs.exit_code}]]'
        )
        return {'role': 'user', 'content': content}
    elif (
            isinstance(obs, CreateFileObservation)
            or isinstance(obs, ReadFileObservation)
            or isinstance(obs, WriteFileObservation)
        ):
        content = 'OBSERVATION:\n' + obs.content
        content = truncate_observation(content)
        return {'role': 'user', 'content': content}

    return None


def load_history(messages: list[dict[str, str]], history: list[tuple[Action, Observation]]):
    for prev_action, obs in history:
        action_message = get_action_message(prev_action)
        if action_message:
            messages.append(action_message)

        obs_message = get_observation_message(obs)
        if obs_message:
            messages.append(obs_message)


def handle_latest_user_message(messages: list[dict[str, str]], turns_left: int):
    latest_user_message = [m for m in messages if m['role'] == 'user'][-1]

    if latest_user_message:
        if latest_user_message['content'].strip() == '/exit':
            return AgentFinishAction()
        latest_user_message['content'] += (
            f'\n\nENVIRONMENT REMINDER: You have {turns_left} turns left to complete the task.'
        )
    
    return latest_user_message


def get_system_message() -> str:
    return f'{SYSTEM_PREFIX}\n\n{COMMAND_DOCS}\n\n{SYSTEM_SUFFIX}'


def get_in_context_example() -> str:
    return EXAMPLES


class VSCodeActAgent(Agent):
  VERSION = '0.1.0'
  
  system_message: str = get_system_message()
  in_context_example: str = f"Here is an example of how you can interact with the environment for task solving:\n{get_in_context_example()}\n\nNOW, LET'S START!"

  def __init__(
    self,
    llm: LLM,
) -> None:
    super().__init__(llm)
    self.reset()


  def reset(self) -> None:
      """
      Resets the agent.
      """
      super().reset()

  def search_memory(self, query: str) -> list[str]:
      raise NotImplementedError('Implement this abstract method')
  

  def step(self, state: State) -> Action:
    """
    Performs one step using the VSCodeAct agent.
    This includes gathering info on previous steps and prompting the model to make a command to execute.

    Parameters:
    - state (State): used to get updated info and background commands

    Returns:
    - CmdRunAction(command) - bash command to run
    - IPythonRunCellAction(code) - IPython code to run
    - BrowseInteractiveAction(browsergym_command) - BrowserGym commands to run
    - MessageAction(content) - Message action to run (e.g. ask for clarification)
    - AgentFinishAction() - end the interaction
    """
    messages: list[dict[str, str]] = [
        {'role': 'system', 'content': self.system_message},
        {'role': 'user', 'content': self.in_context_example},
    ]

    load_history(messages, state.history)
    handle_latest_user_message(messages, state.max_iterations - state.iteration)

    response = self.llm.do_completion(
        messages=messages,
        stop=[
            '</execute_editor>',
            '</execute_bash>',
        ],
        temperature=0.0,
    )

    action_str = parse_response(response)
    state.num_of_chars += sum(
        len(message['content']) for message in messages
    ) + len(action_str)

    if finish_command := re.search(r'<finish>.*</finish>', action_str, re.DOTALL):
        thought = action_str.replace(finish_command.group(0), '').strip()
        return AgentFinishAction(thought=thought)
    if bash_command := re.search(
        r'<execute_bash>(.*?)</execute_bash>', action_str, re.DOTALL
    ):
        # remove the command from the action string to get thought
        thought = action_str.replace(bash_command.group(0), '').strip()
        # a command was found
        command_group = bash_command.group(1).strip()

        if command_group.strip() == 'exit':
            return AgentFinishAction()
        return CmdRunAction(command=command_group, thought=thought)
    elif python_code := re.search(
        r'<execute_editor>(.*?)</execute_editor>', action_str, re.DOTALL
    ):
        # a code block was found
        data = python_code.group(1).strip()
        thought = action_str.replace(python_code.group(0), '').strip()
        parsed = handleEditorAction(data)

        match parsed.operation:
            case 'create':
                return CreateFileAction(path=parsed.filename, thought=thought)
            case 'open':
                return ReadFileAction(path=parsed.filename, thought=thought)
            case 'edit':
                return WriteFileAction(
                    path=parsed.filename,
                    start=int(parsed.start),
                    stop=int(parsed.end),
                    content=parsed.content,
                    thought=thought,
                )
            case _:
                return MessageAction(content='Invalid editor operation', wait_for_response=True)
    else:
        # We assume the LLM is GOOD enough that when it returns pure natural language
        # it want to talk to the user
        return MessageAction(content=action_str, wait_for_response=True)



def handleEditorAction(raw: str) -> dict[str, str]:
    operation = re.search(r'<operation>(.*?)</operation>', raw, re.DOTALL).group(1)
    filename = re.search(r'<filename>(.*?)</filename>', raw, re.DOTALL).group(1)

    if operation == 'create' or operation == 'open':
        return {'operation': operation, 'filename': filename}
    elif operation == 'edit':
        start = re.search(r'<start>(.*?)</start>', raw, re.DOTALL).group(1)
        end = re.search(r'<end>(.*?)</end>', raw, re.DOTALL).group(1)
        content = re.search(r'<content>(.*?)</content>', raw, re.DOTALL).group(1)
        return {'operation': operation, 'filename': filename, 'start': start, 'end': end, 'content': content}
    
    # TODO: Perhaps return ValueError instead
    return None

import re
from agenthub.codeact_agent.utils import handle_latest_user_message, handleEditorAction, load_history, parse_response
from opendevin.events.action.commands import CmdRunAction
from opendevin.events.action.editor import CreateFileAction, ReadFileAction, UpdateFileAction
from opendevin.events.action.message import MessageAction
from opendevin.llm.llm import LLM
from opendevin.controller.agent import Agent
from opendevin.controller.state.state import State
from opendevin.events.action import Action, AgentFinishAction
from agenthub.codeact_agent.vscode_prompt import (
    SYSTEM_PREFIX,
    COMMAND_DOCS,
    SYSTEM_SUFFIX,
    EXAMPLES,
)


def get_system_message() -> str:
    return f'{SYSTEM_PREFIX}\n\n{COMMAND_DOCS}\n\n{SYSTEM_SUFFIX}'


def get_in_context_example() -> str:
    return EXAMPLES


class VSCodeActAgent(Agent):
  VERSION = '0.1.1'
  
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
        match parsed.get('operation'):
            case 'create':
                return CreateFileAction(path=parsed.get('path'), thought=thought)
            case 'read':
                return ReadFileAction(path=parsed.get('path'), thought=thought)
            case 'update':
                return UpdateFileAction(
                    path=parsed.get('path'),
                    start=int(parsed.get('start')),
                    stop=int(parsed.get('stop')),
                    content=parsed.get('content'),
                    thought=thought,
                )
            case _:
                return MessageAction(content='Invalid editor operation', wait_for_response=True)
    else:
        # We assume the LLM is GOOD enough that when it returns pure natural language
        # it want to talk to the user
        return MessageAction(content=action_str, wait_for_response=True)

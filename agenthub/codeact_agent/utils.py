import re
from opendevin.events.observation.commands import CmdOutputObservation
from opendevin.events.observation.editor import CreateFileObservation, ReadFileObservation, UpdateFileObservation
from opendevin.events.observation import Observation
from opendevin.events.action.commands import CmdRunAction
from opendevin.events.action.editor import CreateFileAction, ReadFileAction, UpdateFileAction
from opendevin.events.action.message import MessageAction
from opendevin.events.action import Action, AgentFinishAction

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
    """
    Convert the action to a string representation.
    """
    if isinstance(action, CmdRunAction):
        return f'{action.thought}\n<execute_bash>\n{action.command}\n</execute_bash>'
    elif isinstance(action, CreateFileAction) or isinstance(action, ReadFileAction):
        return f'{action.thought}\n<execute_editor>\n<operation>create</operation><path>{action.path}</path>\n</execute_editor>'
    elif isinstance(action, UpdateFileAction):
        return f'{action.thought}\n<execute_editor>\n<operation>edit</operation><path>{action.path}</path><start>{action.start}</start><stop>{action.stop}</stop><content>{action.content}</content>\n</execute_editor>'
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
    """
    Get the message for the action to be stored in the messages list.
    """
    if (
        isinstance(action, CreateFileAction)
        or isinstance(action, ReadFileAction)
        or isinstance(action, UpdateFileAction)
        or isinstance(action, CmdRunAction)
        or isinstance(action, MessageAction)
    ):
        return {
            'role': 'user' if action.source == 'user' else 'assistant',
            'content': action_to_str(action),
        }

    return None


def get_observation_message(obs) -> dict[str, str] | None:
    """
    Get the message for the observation to be stored in the messages list.
    """
    if isinstance(obs, CmdOutputObservation):
        content = 'OBSERVATION:\n' + truncate_observation(obs.content)
        content += (
            f'\n[Command {obs.command_id} finished with exit code {obs.exit_code}]]'
        )
        return {'role': 'user', 'content': content}
    elif (
            isinstance(obs, CreateFileObservation)
            or isinstance(obs, ReadFileObservation)
            or isinstance(obs, UpdateFileObservation)
        ):
        content = 'OBSERVATION:\n' + obs.content
        content = truncate_observation(content)
        return {'role': 'user', 'content': content}

    return None


def load_history(messages: list[dict[str, str]], history: list[tuple[Action, Observation]]):
    """
    Load the history of actions and observations into the messages list.
    """
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


def handleEditorAction(raw: str) -> dict[str, str]:
    """
    Parse the editor action XML snippet and return the operation, path, start, stop, and content.
    """
    operation = re.search(r'<operation>(.*?)</operation>', raw, re.DOTALL).group(1)
    path = re.search(r'<path>(.*?)</path>', raw, re.DOTALL).group(1)

    if operation == 'create' or operation == 'read':
        return {'operation': operation, 'path': path}
    elif operation == 'update' or operation == 'edit': # OD seems to like using 'edit' rather than 'update' sometimes, even though its not defined
        start = re.search(r'<start>(.*?)</start>', raw, re.DOTALL).group(1)
        stop = re.search(r'<stop>(.*?)</stop>', raw, re.DOTALL).group(1)
        content = re.search(r'<content>(.*?)</content>', raw, re.DOTALL).group(1)
        return {'operation': operation, 'path': path, 'start': start, 'stop': stop, 'content': content}
    
    # TODO: Perhaps return ValueError instead
    return None
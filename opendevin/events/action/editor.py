from dataclasses import dataclass
from typing import ClassVar, Optional
from .action import Action

@dataclass
class CreateFileAction(Action):
    path: str
    content: Optional[str] = None
    runnable: ClassVar[bool] = True
    thought: str = ''
    action = 'create'
    
    def __str__(self) -> str:
        return f'**CreateFileAction**\n{self.path}'


@dataclass
class ReadFileAction(Action):
    path: str
    runnable: ClassVar[bool] = True
    thought: str = ''
    action = 'read'
    
    def __str__(self) -> str:
        return f'**ReadFileAction**\n{self.path}'
    

@dataclass
class UpdateFileAction(Action):
    path: str
    content: str
    start: int = 0
    stop: int = -1 # -1 means end of file
    runnable: ClassVar[bool] = True
    thought: str = ''
    action = 'update'
    
    def __str__(self) -> str:
        return f'**UpdateFileAction**\n{self.path}'

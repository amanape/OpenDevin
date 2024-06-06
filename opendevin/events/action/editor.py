from dataclasses import dataclass
from typing import ClassVar, Optional
from .action import Action

@dataclass
class CreateFileAction(Action):
    path: str
    content: Optional[str] = None
    runnable: ClassVar[bool] = True
    thought: str = ''
    
    def __str__(self) -> str:
        return f'**CreateFileAction**\n{self.path}'


@dataclass
class ReadFileAction(Action):
    path: str
    runnable: ClassVar[bool] = True
    thought: str = ''
    
    def __str__(self) -> str:
        return f'**ReadFileAction**\n{self.path}'
    

@dataclass
class WriteFileAction(Action):
    path: str
    start: int = 0
    stop: int = -1 # -1 means end of file
    content: str
    runnable: ClassVar[bool] = True
    thought: str = ''
    
    def __str__(self) -> str:
        return f'**WriteFileAction**\n{self.path}'

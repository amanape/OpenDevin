from dataclasses import dataclass
from typing import Optional
from .observation import Observation

@dataclass
class CreateFileObservation(Observation):
    path: str
    success: bool
    observation = 'create'
    
    def __str__(self) -> str:
        return f'**CreateFileObservation**\nsuccess: {self.success}\npath: {self.path}'


@dataclass
class ReadFileObservation(Observation):
    path: str
    observation = 'read'
    
    def __str__(self) -> str:
        return f'**ReadFileObservation**\n{self.content}'
    

@dataclass
class UpdateFileObservation(Observation):
    path: str
    success: bool
    observation = 'update'
    
    def __str__(self) -> str:
        return f'**UpdateFileObservation**\nsuccess: {self.success}\npath: {self.path}'

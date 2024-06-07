from dataclasses import dataclass
from typing import Optional
from .observation import Observation

@dataclass
class CreateFileObservation(Observation):
    observation = 'create'
    
    def __str__(self) -> str:
        return f'**CreateFileObservation**\ncontent: {self.content}'


@dataclass
class ReadFileObservation(Observation):
    observation = 'read'
    
    def __str__(self) -> str:
        return f'**ReadFileObservation**\n{self.content}'
    

@dataclass
class UpdateFileObservation(Observation):
    observation = 'update'
    
    def __str__(self) -> str:
        return f'**UpdateFileObservation**\ncode: {self.content}'

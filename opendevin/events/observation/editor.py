from dataclasses import dataclass
from typing import Optional
from .observation import Observation

@dataclass
class CreateFileObservation(Observation):
    path: str
    success: bool
    
    def __str__(self) -> str:
        return f'**CreateFileObservation**\nsuccess: {self.success}\npath: {self.path}'


@dataclass
class ReadFileObservation(Observation):
    path: str
    
    def __str__(self) -> str:
        return f'**ReadFileObservation**\n{self.content}'
    

@dataclass
class WriteFileObservation(Observation):
    path: str
    success: bool
    
    def __str__(self) -> str:
        return f'**WriteFileObservation**\nsuccess: {self.success}\npath: {self.path}{f"\ncontent: {self.content}" if self.content else ""}'

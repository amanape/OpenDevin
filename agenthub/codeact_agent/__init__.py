from opendevin.controller.agent import Agent

from .codeact_agent import CodeActAgent
from .vscodeact_agent import VSCodeActAgent

Agent.register('CodeActAgent', CodeActAgent)
Agent.register('VSCodeActAgent', VSCodeActAgent)

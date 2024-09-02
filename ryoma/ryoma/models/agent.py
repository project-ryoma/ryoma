from enum import Enum


class AgentType(Enum):
    ryoma = "ryoma"
    base = "base"
    embedding = "embedding"
    workflow = "workflow"
    custom = "custom"

from enum import Enum


class AgentType(Enum):
    ryoma = "ryoma_ai"
    base = "base"
    embedding = "embedding"
    workflow = "workflow"
    custom = "custom"

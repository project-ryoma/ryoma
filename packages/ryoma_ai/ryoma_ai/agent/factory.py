from enum import Enum
from typing import Union

from ryoma_ai.agent.arrow_agent import ArrowAgent
from ryoma_ai.agent.base import ChatAgent
from ryoma_ai.agent.embedding import EmbeddingAgent
from ryoma_ai.agent.pandas_agent import PandasAgent
from ryoma_ai.agent.python_agent import PythonAgent
from ryoma_ai.agent.spark_agent import SparkAgent
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.agent.workflow import WorkflowAgent


class AgentProvider(Enum):
    base = ChatAgent
    sql = SqlAgent
    pandas = PandasAgent
    pyarrow = ArrowAgent
    pyspark = SparkAgent
    python = PythonAgent
    embedding = EmbeddingAgent


def get_builtin_agents():
    return list(AgentProvider)


class AgentFactory:
    @staticmethod
    def create_agent(
        agent_type: str, *args, **kwargs
    ) -> Union[EmbeddingAgent, ChatAgent, WorkflowAgent]:
        if not agent_type or not hasattr(AgentProvider, agent_type):
            agent_class = ChatAgent
        else:
            agent_class = AgentProvider[agent_type].value
        return agent_class(*args, **kwargs)

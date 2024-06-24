from enum import Enum

from aita.agent.arrow_agent import ArrowAgent
from aita.agent.base import AitaAgent
from aita.agent.pandas_agent import PandasAgent
from aita.agent.python_agent import PythonAgent
from aita.agent.spark_agent import SparkAgent
from aita.agent.sql import SqlAgent


class AgentProvider(Enum):
    sql = SqlAgent
    pandas = PandasAgent
    pyarrow = ArrowAgent
    pyspark = SparkAgent
    python = PythonAgent


def get_supported_agents():
    return list(AgentProvider)


class AgentFactory:

    @staticmethod
    def create_agent(agent_type: str, *args, **kwargs) -> AitaAgent:
        if not agent_type or not hasattr(AgentProvider, agent_type):
            agent_class = AitaAgent
        else:
            agent_class = AgentProvider[agent_type].value
        return agent_class(*args, **kwargs)

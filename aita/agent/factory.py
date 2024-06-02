from enum import Enum

from aita.agent.base import AitaAgent
from aita.agent.pandas import PandasAgent
from aita.agent.pyarrow import PyArrowAgent
from aita.agent.pyspark import PySparkAgent
from aita.agent.python import PythonAgent
from aita.agent.sql import SqlAgent


class AgentProvider(Enum):
    sql = SqlAgent
    pandas = PandasAgent
    pyarrow = PyArrowAgent
    pyspark = PySparkAgent
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

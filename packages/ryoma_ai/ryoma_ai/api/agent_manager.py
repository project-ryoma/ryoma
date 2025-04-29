from ryoma_ai.agent.arrow_agent import ArrowAgent
from ryoma_ai.agent.base import ChatAgent
from ryoma_ai.agent.pandas_agent import PandasAgent
from ryoma_ai.agent.spark_agent import SparkAgent


class AgentManager:
    """
    Builds agents dynamically based on execution context or user config.
    """

    def __init__(self):
        self._registry = {
            "spark": SparkAgent,
            "pandas": PandasAgent,
            "arrow": ArrowAgent,
        }

    def build_from_context(self, context: dict) -> ChatAgent:
        """
        Expected context:
        {
            "type": "pandas",       # or "spark", "arrow"
            "datasource": <conn>,   # e.g. duckdb_conn, spark_session, etc.
            "config": {...}         # optional agent config
        }
        """
        agent_type = context.get("type")
        agent_cls = self._registry.get(agent_type)

        if not agent_cls:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        return agent_cls.from_context(context)

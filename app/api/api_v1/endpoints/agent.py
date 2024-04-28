from typing import Any, Union

import json

from fastapi import APIRouter

from aita.agent import PandasAgent, PythonAgent, SqlAgent
from aita.datasource.base import SqlDataSource
from aita.datasource.snowflake import SnowflakeDataSource
from app.api.deps import SessionDep
from app.crud import crud_datasource
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChatResponseStatus,
    RunToolRequest,
    RunToolResponse,
)

router = APIRouter()


def get_datasource(session: SessionDep):
    # datasource = crud_datasource.get_by_id(session=session, id=chat_request.datasource_id)
    datasource = SnowflakeDataSource(
        user="AITA",
        password="Xh!0135259098",
        account="qlezend-pu83508",
        warehouse="COMPUTE_WH",
        database="SNOWFLAKE_SAMPLE_DATA",
        schema="TPCH_SF1",
        role="PUBLIC_ROLE",
    )
    datasource.connected = True
    if not datasource or not datasource.connected:
        return ChatResponse(
            status=ChatResponseStatus.error,
            message="Datasource not connected, Please connect to a datasource before using the agent.",
        )
    return datasource


def get_agent(chat_request: Union[ChatRequest, RunToolRequest], datasource: SqlDataSource):
    if chat_request.agent == "sql":
        agent = SqlAgent(
            datasource=datasource,
            model=chat_request.model,
            temperature=chat_request.temperature,
        )
    elif chat_request.agent == "panadas":
        df = datasource.to_pandas("SELECT * FROM CUSTOMER")
        agent = PandasAgent(
            dataframes={"CUSTOMER": df},
            model=chat_request.model,
            temperature=chat_request.temperature,
        )
    else:
        return ChatResponse(status=ChatResponseStatus.error, message="Agent not supported.")
    return agent


@router.post("/chat", response_model=ChatResponse)
def chat(*, session: SessionDep, chat_request: ChatRequest) -> Any:
    datasource = get_datasource(session)
    agent = get_agent(chat_request, datasource)
    response = agent.chat(
        question=chat_request.prompt,
    )
    additional_info = None
    if "tool_calls" in response.additional_kwargs:
        function_call = response.additional_kwargs["tool_calls"][0]["function"]
        additional_info = {
            "name": function_call["name"],
            "arguments": json.loads(function_call["arguments"]),
        }
    return ChatResponse(
        status=ChatResponseStatus.success, message=response.content, additional_info=additional_info
    )


@router.post("/run_tool", response_model=RunToolResponse)
def run_tool(*, session: SessionDep, run_tool_request: RunToolRequest) -> Any:
    datasource = get_datasource(session)
    agent = get_agent(run_tool_request, datasource)
    response = agent.run_tool({"name": run_tool_request.name, "args": run_tool_request.arguments})
    return RunToolResponse(status=ChatResponseStatus.success, message=str(response))

from typing import Any

from fastapi import APIRouter

from aita.agent import AitaSqlAgent
from app.api.deps import SessionDep
from app.schemas import ChatResponse, ChatRequest, ChatResponseStatus
from app.crud import crud_database

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(*, session: SessionDep, chat_request: ChatRequest) -> Any:
    if chat_request.agent == "sql":
        if not chat_request.datasource:
            return ChatResponse(
                status=ChatResponseStatus.error,
                message="Sql agent requires to specify a data source, please try connect to a data source and try "
                        "again."
            )

        database = crud_database.get_by_id(session=session, id=chat_request.database_id)
        if not database or not database.connected:
            return ChatResponse(
                status=ChatResponseStatus.error,
                message="Datasource not connected, Please connect to a datasource before using the agent."
            )

        agent = AitaSqlAgent(
            database=database,
            model=chat_request.model,
            temperature=chat_request.temperature,
        )

        response = agent.chat(
            question=chat_request.prompt,
            allow_call_tool=chat_request.allow_function_calls
        )
        return ChatResponse(
            status=ChatResponseStatus.success,
            message=response
        )
    else:
        return ChatResponse(
            status=ChatResponseStatus.error,
            message="Agent not supported."
        )

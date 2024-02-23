import importlib
from fastapi import APIRouter

from app.models import ToolUseRequest, ToolUseResponse
from aita.utils import run_tool

router = APIRouter()


@router.post("/run")
def run(tool_use_request: ToolUseRequest) -> ToolUseResponse:
    res = run_tool(tool_use_request.name, tool_use_request.arguments)
    return ToolUseResponse(
        status="Success",
        message=res.choices[0].message.content
    )

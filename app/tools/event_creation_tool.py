from langchain_core.tools import BaseTool
from typing import TypedDict, Type, List
import subprocess
from langchain.pydantic_v1 import BaseModel, Field


class CommandResult(TypedDict):
    stdout: str
    stderr: str

class EventCreationArguments(BaseModel):
    events: List[str] = Field(description="The list events to register")


class EventCreationTool(BaseTool):
    name: str = "event_creation_tool"
    description: str = "A tool to register events to database." # Dummy description. This tool does not execute actual registration..
    args_schema: Type[BaseModel] = EventCreationArguments
    terminate_agent: bool = True
    events = []

    def _run(self, *args, **kwargs) -> None:
        self.events = kwargs["events"]
        return None

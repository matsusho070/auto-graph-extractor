from langchain_core.tools import BaseTool
from typing import TypedDict, Type, List
import subprocess
from langchain.pydantic_v1 import BaseModel, Field

class EventExtraction(BaseModel):
    event_name: str = Field(description="The name of the event")
    original_phrase: str = Field(description="The original phrase in the original article where the event is mentioned")

class EventCreationArguments(BaseModel):
    events: List[EventExtraction] = Field(description="The list of extraction of events from the text.")


class EventCreationTool(BaseTool):
    name: str = "event_creation_tool"
    description: str = "A tool to register events to database." # Dummy description. This tool does not execute actual registration..
    args_schema: Type[BaseModel] = EventCreationArguments
    terminate_agent: bool = True
    events = []

    def _run(self, *args, **kwargs) -> None:
        event_names = list(map(lambda event: event["event_name"], self.events))
        self.events += list(filter(lambda event: event["event_name"] not in event_names, kwargs["events"]))
        return None

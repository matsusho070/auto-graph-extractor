from langchain_core.tools import BaseTool
from typing import TypedDict, Dict, Type
from langchain.pydantic_v1 import BaseModel, Field

class Arguments(BaseModel):
    score: int = Field(description="The score of the extraction")
    event_name: str = Field(description="The name of the extracted event")

class ScoreRegistrationTool(BaseTool):
    name: str = "score_registration_tool"
    description: str = "A tool to register extraction score to database." # Dummy description. This tool does not execute actual registration..
    args_schema: Type[BaseModel] = Arguments
    terminate_agent: bool = True
    scores = {}

    def _run(self, *args, **kwargs) -> None:
        self.scores[kwargs["event_name"]] = kwargs["score"]
        return None

from langchain_core.tools import BaseTool
from typing import TypedDict, Type, List, Dict
import subprocess
from langchain.pydantic_v1 import BaseModel, Field


class RelatinoshipRegistrationArguments(BaseModel):
    cause: str = Field(description="The cause of the relation")
    effect: str = Field(description="The effect of the relation")

class RelationResgirstrationTool(BaseTool):
    name: str = "relation_registration_tool"
    description: str = "A tool to register relations to database." # Dummy description. This tool does not execute actual registration..
    args_schema: Type[BaseModel] = RelatinoshipRegistrationArguments
    relations = []

    def _run(self, *args, **kwargs) -> None:
        self.relations.append((kwargs["cause"], kwargs["effect"]))
        return True

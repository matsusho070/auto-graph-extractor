from langchain_core.tools import BaseTool
from typing import TypedDict, Type, List, Dict
import subprocess
from langchain.pydantic_v1 import BaseModel, Field


class RelatinoshipRegistrationArguments(BaseModel):
    cause: str = Field(description="The cause of the relationship")
    effect: str = Field(description="The effect of the relationship")

class RelationshipResgirstrationTool(BaseTool):
    name: str = "relationship_registration_tool"
    description: str = "A tool to register relationships to database." # Dummy description. This tool does not execute actual registration..
    args_schema: Type[BaseModel] = RelatinoshipRegistrationArguments
    relationships = []

    def _run(self, *args, **kwargs) -> None:
        self.relationships.append((kwargs["cause"], kwargs["effect"]))
        return True

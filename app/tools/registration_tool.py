from langchain_core.tools import BaseTool
from typing import Type, List
from langchain.pydantic_v1 import BaseModel, Field, Extra

class Arguments(BaseModel):
    pass

class RegistrationTool(BaseTool):
    name: str = "registration_tool"
    description: str = "A tool to register events to database." # Dummy description. This tool does not execute actual registration..
    args_schema: Type[BaseModel] = Arguments
    terminate_agent: bool = True

    class Config:
      extra = Extra.allow

    def _run(self, *args, **kwargs) -> None:
        self.terminated = True
        return None

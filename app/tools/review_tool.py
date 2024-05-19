from langchain_core.tools import BaseTool
from typing import TypedDict, Type, List
import subprocess
from util import create_prompt_from_template, ask_task
from langchain.pydantic_v1 import BaseModel, Field, Extra
from langchain_core.language_models.chat_models import BaseChatModel


class ReviewArguments(BaseModel):
    events: List[str] = Field(description="The list of extracted events")

class Reviewer(BaseTool):
    name: str = "reviewer_tool"
    description: str = "A tool that review the result of the event creation tool."
    args_schema: Type[BaseModel] = ReviewArguments

    class Config:
      extra = Extra.allow

    def __init__(self, llm, article):
        super().__init__()
        self.llm = llm
        self.article = article

    def _run(self, *args, **kwargs) -> str:
        events = kwargs["events"]
        response = ask_task(self.llm, [], create_prompt_from_template("review_events.jinja", article=self.article, events=events))
        return response.content

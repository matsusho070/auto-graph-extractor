from langchain_core.tools import BaseTool
from typing import TypedDict, Type, List
import subprocess
from util import create_prompt_from_template, ask_task
from langchain.pydantic_v1 import BaseModel, Field, Extra
from langchain_core.language_models.chat_models import BaseChatModel


class EventReviewArguments(BaseModel):
    events: List[str] = Field(description="The list of extracted events")

class EventReviewer(BaseTool):
    name: str = "event_reviewer_tool"
    description: str = "A tool that review the result of the event creation tool."
    args_schema: Type[BaseModel] = EventReviewArguments

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


class Relationship(TypedDict):
    source: str = Field(description="The name of the event that is the source of the relationship")
    target: str = Field(description="The name of the event that is the target of the relationship")

class RelationshipReviewArguments(BaseModel):
    relationships: List[Relationship] = Field(description="The list of extracted relationships")

class RelationshipReviewer(BaseTool):
    name: str = "relationship_reviewer"
    description: str = "A tool to register extracted relationships to database."
    args_schema: Type[BaseModel] = RelationshipReviewArguments

    class Config:
      extra = Extra.allow

    def __init__(self, llm, article):
        super().__init__()
        self.llm = llm
        self.article = article

    def _run(self, *args, **kwargs) -> None:
        relationships = kwargs["relationships"]
        response = ask_task(self.llm, [], create_prompt_from_template("review_relationships.jinja", article=self.article, relationships=relationships))
        return response.content

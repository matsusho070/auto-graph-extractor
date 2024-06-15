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
        message_history = kwargs["message_history"]
        response = ask_task(self.llm, [], create_prompt_from_template("review_events.jinja", article=self.article, events=events), message_history)
        return response.content


class Relation(TypedDict):
    source: str = Field(description="The name of the event that is the source of the relation")
    target: str = Field(description="The name of the event that is the target of the relation")

class RelationReviewArguments(BaseModel):
    relations: List[Relation] = Field(description="The list of extracted relations")

class RelationReviewer(BaseTool):
    name: str = "relation_reviewer"
    description: str = "A tool to register extracted relations to database."
    args_schema: Type[BaseModel] = RelationReviewArguments

    class Config:
      extra = Extra.allow

    def __init__(self, llm, article):
        super().__init__()
        self.llm = llm
        self.article = article

    def _run(self, *args, **kwargs) -> None:
        relations = kwargs["relations"]
        messages = ask_task(self.llm, [], create_prompt_from_template("review_relations.jinja", article=self.article, relations=relations))
        return messages[-1].content

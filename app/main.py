import os
import openai
from langsmith import Client
from langchain_openai import ChatOpenAI
from tools.event_creation_tool import EventCreationTool
from tools.review_tool import Reviewer
from langchain_core.messages import HumanMessage, SystemMessage
from util import create_prompt_from_template, ask_task
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
import argparse
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate



def main(use_cache, article_text, model_name):
    set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    # Initialize Lang Smith
    client = Client()

    llm = ChatOpenAI(model_name=model_name, temperature=0.7, cache=use_cache)

    existing_event_list = ["地震", "台風", "洪水", "火事"]
    event_creation_tool = EventCreationTool()

    tools = [event_creation_tool, Reviewer(llm, article_text)]
    ask_task(llm, tools, create_prompt_from_template("extract_events.jinja",
                                                     article=article_text,
                                                      existing_event_list="\n".join(list(map(lambda event_str: '* ' + event_str, existing_event_list)))))

    print("events:" , event_creation_tool.events)
    return
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process workspace directory')
    parser.add_argument('--no_cache', action='store_true', help='Invalidate cache')
    parser.add_argument('--model_name', type=str, default="gpt-4o", help='Model name')
    args = parser.parse_args()
    # Read from stdin
    article_text = input("Enter article text: ")


    main(not args.no_cache, article_text, args.model_name)
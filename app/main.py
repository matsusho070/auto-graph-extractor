import os
import openai
import json
import sys
from langsmith import Client
from langchain_openai import ChatOpenAI
from tools.event_creation_tool import EventCreationTool
from tools.relation_registration_tool import RelationResgirstrationTool
from tools.review_tool import EventReviewer, RelationReviewer
from langchain_core.messages import HumanMessage, SystemMessage
from util import create_prompt_from_template, ask_task
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
import argparse
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate



def main(use_cache, article_text, model_name, target_file):
    if(use_cache):
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    # Initialize Lang Smith
    client = Client()

    llm = ChatOpenAI(model_name=model_name, temperature=0.7, cache=use_cache)

    existing_event_list = ["地震", "台風", "洪水", "火事"]
    event_creation_tool = EventCreationTool()

    tools = [event_creation_tool, EventReviewer(llm, article_text)]
    ask_task(llm, tools, create_prompt_from_template("extract_events.jinja",
                                                     article=article_text,
                                                      existing_event_list="\n".join(list(map(lambda event_str: '* ' + event_str, existing_event_list)))))

    print("events:" , event_creation_tool.events, file=sys.stderr)


    relation_registration_tool = RelationResgirstrationTool()

    tools = [relation_registration_tool, RelationReviewer(llm, article_text)]

    ask_task(llm, tools, create_prompt_from_template("extract_relations.jinja",
                                                     article=article_text,
                                                     events=list(map(lambda event: event["event_name"], event_creation_tool.events))))


    print("relations:", relation_registration_tool.relations, file=sys.stderr)

    # Create image that shows the original article and the extracted events and relations
    
    nodes = list(map(lambda event: {"id": event["event_name"],
                                    "labels": [],
                                    "properties": {},
                                     "original_phrase": event["original_phrase"]}, event_creation_tool.events))

    print(json.dumps({
        "article": article_text,
        "nodes": nodes,
        "edges": list(map(lambda relation: {"from": relation[0],
                                             "to": relation[1],
                                             "labels": [],
                                                "properties": {},
                                             }, relation_registration_tool.relations))
    }, ensure_ascii=False, indent=2), file=target_file)
    
    print(json.dumps({
        "nodes": list(map(lambda event: event["event_name"], event_creation_tool.events)),
        "edges": list(map(lambda relation: {"from": relation[0],
                                             "to": relation[1],
                                             }, relation_registration_tool.relations))
    }, ensure_ascii=False, indent=2), file=open("output_log.json", "w"))

    return
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process workspace directory')
    parser.add_argument('--no_cache', action='store_true', help='Invalidate cache')
    parser.add_argument('--model_name', type=str, default="gpt-4o", help='Model name')
    parser.add_argument('-o', type=str, default="output.json", help='The output file name')
    args = parser.parse_args()
    # Read from stdin
    article_text = sys.stdin.read()

    target_file = open(args.o, "w")
    main(not args.no_cache, article_text, args.model_name, target_file)
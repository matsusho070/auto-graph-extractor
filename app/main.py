import os
import openai
import json
import sys
from langsmith import Client
from langchain_openai import ChatOpenAI
from tools.registration_tool import RegistrationTool
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
from sqc_score import calc_sqc_score


def main(use_cache, article_text, model_name, target_file, golden_answer_file):
    if(use_cache):
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    # Initialize Lang Smith
    client = Client()

    llm = ChatOpenAI(model_name=model_name, temperature=0.7, cache=use_cache)

    existing_event_list = ["地震", "台風", "洪水", "火事"]
    event_creation_tool = EventCreationTool()

    messages = []

    registration_tool = RegistrationTool()
    review_count = 0
    while True:
        messages = ask_task(llm, [], create_prompt_from_template("extract_events.jinja",
                                                        article=article_text,
                                                        existing_event_list="\n".join(list(map(lambda event_str: '* ' + event_str, existing_event_list))),
                                                        ), messages, use_cache)

        messages = ask_task(llm, [registration_tool], 
                            create_prompt_from_template("review_events.jinja"),
                             messages, use_cache=use_cache)
        review_count += 1
        if registration_tool.terminated or review_count >= 5:
            break
        
    
    ask_task(llm, [event_creation_tool], create_prompt_from_template("conclude_extraction.jinja"), messages, use_cache)

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
    
    event_names = list(map(lambda event: event["event_name"], event_creation_tool.events))
    print(json.dumps({
        "nodes": event_names,
        "edges": list(map(lambda relation: {"from": relation[0],
                                             "to": relation[1],
                                             }, relation_registration_tool.relations))
    }, ensure_ascii=False, indent=2), file=open("output_log.json", "w"))

    if golden_answer_file:
        golden_answer = json.load(open(golden_answer_file, 'r')) 
        calc_sqc_score(use_cache, article_text, {"nodes": event_names}, golden_answer)

    return
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process workspace directory')
    parser.add_argument('--no_cache', action='store_true', help='Invalidate cache')
    parser.add_argument('--model_name', type=str, default="gpt-4o", help='Model name')
    parser.add_argument('--golden-answer', type=str, help='The file containing the golden answer')
    parser.add_argument('-i', '--input-file', type=str, help='The input article file name')
    parser.add_argument('-o', '--output-file', type=str, default="output.json", help='The output file name')
    args = parser.parse_args()
    article_text = open(args.input_file, "r").read()

    target_file = open(args.output_file, "w")
    main(not args.no_cache, article_text, args.model_name, target_file, args.golden_answer)
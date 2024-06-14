# A script to evaluate the quality of event extraction from article.
# Usage: python sqc_score.py <article_text> <extraction_result> <golden_answer_file>

import os
import openai
import json
import sys
from langsmith import Client
from langchain_openai import ChatOpenAI
from tools.score_registration_tool import ScoreRegistrationTool
from tools.relationship_registration_tool import RelationshipResgirstrationTool
from tools.review_tool import EventReviewer
from langchain_core.messages import HumanMessage, SystemMessage
from util import create_prompt_from_template, ask_task
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
import argparse
from langchain_core.prompts import ChatPromptTemplate

def main(use_cache, article_text, extraction_result, golden_answer):
    if(use_cache):
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    # Initialize Lang Smith
    client = Client()

    remaining_nodes = []
    matched_nodes_count = 0
    for node_id in extraction_result['nodes']:
        if node_id in golden_answer['nodes']:
            matched_nodes_count += 1
        else:
            remaining_nodes.append(node_id)

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7, cache=use_cache)
    tool = ScoreRegistrationTool()
    ask_task(llm, [tool], create_prompt_from_template("scoring_extracted_event.jinja",
                                                     article=article_text,
                                                     golden_answers='\n'.join(golden_answer['nodes']),
                                                     events='\n'.join(remaining_nodes)))
    print(f"{len(tool.scores)} scores registered.")
    print(tool.scores)
    print(f"remaining nodes: {len(remaining_nodes)}")
    assert(len(tool.scores) == len(remaining_nodes))
    threshold = 0.8
    partially_correct_scores = [score for score in tool.scores.values() if score >= threshold and score < 1]
    perfect_scores = [score for score in tool.scores.values() if score == 1]
    precision = (matched_nodes_count + len(perfect_scores) + sum(partially_correct_scores)) / len(extraction_result['nodes'])
    print(f"Node precision: {precision}")
    recall = (matched_nodes_count + sum(partially_correct_scores) + len(perfect_scores)) / (len(golden_answer['nodes']) + len(partially_correct_scores))
    print(f"Node recall: {recall}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A script to evaluate the quality of event extraction from article.')
    parser.add_argument('article_text', type=str, help='The text of the article to be evaluated')
    parser.add_argument('extraction_result', type=str, help='The result of extraction')
    parser.add_argument('golden_answer_file', type=str, help='The file containing the golden answer')
    parser.add_argument('--no-cache', action='store_true', help='Invalidate cache')
    args = parser.parse_args()
    article_text = open(args.article_text, 'r').read()
    extraction_result = json.load(open(args.extraction_result, 'r'))
    golden_answer = json.load(open(args.golden_answer_file, 'r'))

    # if extraction_result includes non-unique nodes, exit with error
    if len(extraction_result['nodes']) != len(set(extraction_result['nodes'])):
        print("Error: extraction_result includes non-unique nodes", file=sys.stderr)
        sys.exit(1)
    
    main(not args.no_cache, article_text, extraction_result, golden_answer)
import subprocess
import os
from typing import List
from jinja2 import Environment, FileSystemLoader
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
import openai
import json
import hashlib
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage


prompts_path = os.path.join(os.path.dirname(__file__), "prompts")
file_loader = FileSystemLoader(prompts_path)
jinja_env = Environment(loader=file_loader)


def create_prompt_from_template(template_name: str, **kwargs):
    template = jinja_env.get_template(template_name)
    return template.render(**kwargs)


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__



def print_messages(messages):
    for message in messages:
        if type(message) == AIMessage or (type(message) == dict and message["role"] == "assistant"):
            color_code = "\033[93m"    
            role = "assistant"
        elif type(message) == HumanMessage or (type(message) == dict and message["role"] == "user"):
            color_code = "\033[94m"
            role = "user"
        else:
            color_code = "\033[95m"
            role = "function"
        content = message["content"] if type(message) == dict else message.content

        print(f"{color_code}{role}: {content}\033[0m")
        if type(message) == AIMessage and "tool_calls" in message.additional_kwargs:
            for tool_call in message.additional_kwargs["tool_calls"]:
                print(f"  {color_code}tool: {tool_call['function']['name']}: {tool_call['function']['arguments']}\033[0m")



def ask_task(
        llm: BaseChatModel, tools: List[BaseTool], task_description: str, use_cache: bool = True
):

    messages = [
        {
            "role": "user",
            "content": task_description,
        },
    ]    

    print_messages(messages)
    try:
        while True:
            if tools is not None and len(tools) > 0:
                llm = llm.bind_tools(tools)

            response = llm.invoke(messages)

            print_messages([
                response
            ])
            messages.append(response)

            if "tool_calls" in response.additional_kwargs:
                for tool_call in response.additional_kwargs["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    tool = next(filter(lambda t: t.name == tool_name, tools))
                    result = tool._run(**tool_args)
                    if hasattr(tool, "terminate_agent") and tool.terminate_agent:
                        return result
                    else:
                        new_messages = [
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": json.dumps(result, ensure_ascii=False)
                            }
                        ]
                        print_messages(new_messages)
                        messages = messages + new_messages
            else:
                return response
    except Exception as e:
        print(f"The request to OpenAI API failed. Here is the error message:")
        print(e)
        raise e
    
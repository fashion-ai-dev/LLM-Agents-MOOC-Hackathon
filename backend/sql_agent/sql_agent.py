import uuid

from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from platform_hub.prompt_hub import sql_agent
from build_tools.build_tools import sql_agent_tools
from sql_agent.sql_function import fetch_postgres_data
from utils import parse_tool_output
from platform_hub.logs import store_logs
from globals import user_tokens
from datetime import datetime
from openai_client.connection import OpenAISingleton

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

open_ai = None


async def run_sql_query(
    message, user_input, master_agent_input, sid, message_id, thread_id
):

    agent = "sql_agent"
    log_id = str(uuid.uuid4())

    logs_data = {
        "log_id": log_id,
        "thread_id": thread_id,
        "message_id": message_id,
        "agent_name": agent,
        "user_question": user_input,
        "agent_prompt": message,
        "timestamp": datetime.now().isoformat(),
    }
    await store_logs(sid, logs_data)

    print("SQL Agent", message, "\n\n\n")

    model_settings = {
        "model": "ft:gpt-4o-2024-08-06:fashionai:sql-agent:ApjieCJc",#"ft:gpt-4o-2024-08-06:fashionai:sql-agent-python:ALzCsYgL",  # ft:gpt-4o-2024-08-06:fashionai:sql-agent:ALEkyhlL
        "seed": 1841802839,
        "tools": sql_agent_tools,
        "tool_choice": "required",
        "messages": message,
        "store": True,
        "metadata": {
            "role": "sql_agent",
            "project" : "hackathon",
        },
        "temperature": 0,
    }
    # print(message)
    response = OpenAISingleton.get_instance().client.chat.completions.create(**model_settings)
    # print("SQL Agent response: ",response)

    tool_call = response.choices[0].message.tool_calls[0]
    # comment = response.choices[0].message.content To be implemented in case a conversation happens instead of a tool call
    print("SQL Agent Tool Call: ", tool_call, "\n\n\n")

    # Assistant tool call message generated by the LLM. Notice there is an array of calls. Notice function `arguments` is a JSON string of inputs.
    # ,

    arguments = json.loads(tool_call.function.arguments)
    tool_name = tool_call.function.name
    tool_call_id = tool_call.id

    prompt_tokens = response.usage.prompt_tokens
    reply_tokens = response.usage.completion_tokens

    # Move the import here to avoid circular imports
    from build_tools.trigger_tools import call_tool_function

    tool_output = await call_tool_function(
        tool_name, user_input, arguments, sid, message_id, thread_id
    )

    # user_info = user_tokens.get(sid)

    # # to guarantee model always pass file_url
    # if 'file_url' in tool_output:
    #   user_info['last_file_url'] = tool_output['file_url']
    # else:
    #   tool_output['file_url'] = user_info.get('last_file_url', None)

    logs_data = {
        "log_id": log_id,
        "thread_id": thread_id,
        "message_id": message_id,
        "agent_name": agent,
        "user_question": user_input,
        "agent_response": {"tool_call": tool_name, "tool_input": arguments},
        "code_output": tool_output,
        "agent_prompt": message,
        "prompt_token": prompt_tokens,
        "output_token": reply_tokens + prompt_tokens,
        "completion_tokens": reply_tokens,
        "timestamp": datetime.now().isoformat(),
    }
    await store_logs(sid, logs_data)

    print(
        "SQL Tool output", tool_output
    )  # tool_output = execute_code(arguments['input'],sid)
    # # Parse the chat completion content
    tool_history = [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {"name": tool_name, "arguments": str(arguments)},
                }
            ],
        },
        # Tool result message outputted by the function. Notice content is a JSON string of the tool output in `content`.
        {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": tool_name,
            "content": str(tool_output),
        },
    ]

    return arguments, tool_output, tool_call_id, tool_history, tool_name


async def agent_sql_query(user_input, master_agent_input, sid, message_id, thread_id):

    max_attempts = 3
    attempts = 0

    message = [
        {"role": "system", "content": sql_agent},
        {"role": "user", "content": str(master_agent_input)},
    ]

    while attempts < max_attempts:

        print("SQL Agent Attempt: ", attempts, "\n\n\n")
        # Call the get_sql_query function
        query, output, tool_call_id, tool_history, tool_name = await run_sql_query(
            message, user_input, master_agent_input, sid, message_id, thread_id
        )

        print("SQL Agent tool output", output, "\n\n\n")
        # print("Type output", type(output), "\n\n\n")

        # output = parse_tool_output(output)

        if output["status"] == "failure":
            message.extend(tool_history)
            message.append(
                {
                    "role": "user",
                    "content": "There was an error on previous code. Do fix the previous code based on output message of last tool call.",
                }
            )

        elif output["output"] == "":
            message.extend(tool_history)
            message.append(
                {
                    "role": "user",
                    "content": "The code output of last tool call is empty and does not give you the full data needed to answer. Check if escape characters were used poorly and fix it, if code started with a comment sometimes the string makes it a single line comment. Rewrite your code adding the necessary print statement",
                }
            )
        else:
            return output

        # Increment the attempt counter
        attempts += 1

    # If the loop completes without success, return the last output
    return output


# user_input = 'gere um relatório com a méia de vendas diárias de cada categori em Abril'
# master_agent_input = 'Retrieve the average monthly sales from march to july'
# a = agent_sql_query(user_input, master_agent_input, sid=12, client_id=None, userProfileId=None)
# print(a)

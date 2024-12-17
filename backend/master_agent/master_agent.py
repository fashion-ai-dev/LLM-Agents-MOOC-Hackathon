# https://platform.openai.com/docs/guides/function-calling
import ast
import re

from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from platform_hub.prompt_hub import maestro
from utils import parse_tool_output,parse_sanitize_tool_output
from build_tools.build_tools import master_tools
from platform_hub.logs import store_logs
from build_tools.trigger_tools import call_tool_function
from globals import user_tokens
from datetime import datetime
import uuid
from openai_client.connection import OpenAISingleton

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

open_ai = None


async def run_master_agent(message, user_input, sid, message_id, thread_id):
    log_id = str(uuid.uuid4())
    agent = "Maestro Agent"

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
    # Get the visionoutput string for every product
    # print("Master Prompt:",message,"\n\n\n")
    model_settings = {
        "model": "ft:gpt-4o-2024-08-06:fashionai:maestro-agent:APxYMxS3",
        "seed": 1000,
        "tools": master_tools,
        "tool_choice": {"type": "function", "function": {"name": "plan_scratchpad"}},
        "parallel_tool_calls": False,
        "store": True,
        "metadata": {
            "role": "maestro",
                },
        "messages": message,
        "temperature": 0,
    }

    response = OpenAISingleton.get_instance().client.chat.completions.create(**model_settings)
    # print(response)

    # ChatCompletion(id='chatcmpl-A1FDjs9JGlSmt7E3TSgPTTCGFQrsP', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Hello! How can I assist you today?', refusal=None, role='assistant', function_call=None, tool_calls=None))], created=1724860199, model='gpt-4o-mini-2024-07-18', object='chat.completion', service_tier=None, system_fingerprint='fp_f33667828e', usage=CompletionUsage(completion_tokens=10, prompt_tokens=386, total_tokens=396))

    tool_call = response.choices[0].message.tool_calls[0]
    print("Master agent tool call: ", tool_call, "\n")

    plan = parse_sanitize_tool_output(tool_call.function.arguments)
    print("Plan  :", plan)

    # If Agent calls plan_scratchpad as next tool to update the plan
    if plan["next_tool"] == "plan_scratchpad":
        plan = json.loads(plan["next_tool_arguments"])
        print("Updated Plan (from plan_scratchpad): ", plan)

    tool_name = plan["next_tool"]
    print("Next Tool Call: ", tool_name)

    # Extract next_tool_arguments from the plan
    master_agent_input = plan["next_tool_arguments"]

    # Parse and sanitize the input
    master_agent_input_parsed = parse_sanitize_tool_output(master_agent_input)

    # Ensure the parsed input is a dictionary
    if isinstance(master_agent_input_parsed, str):
        master_agent_input_logs = json.loads(master_agent_input_parsed)
    elif isinstance(master_agent_input_parsed, dict):
        master_agent_input_logs = master_agent_input_parsed
    else:
        raise ValueError(
            "Unexpected type for master_agent_input_parsed. Expected str or dict, got: "
            + str(type(master_agent_input_parsed))
        )

    # Extract 'input' value
    input_value = master_agent_input_logs["input"]
    print("Input: ",input_value)

    # Determine if input_value is already a dict or needs parsing
    if isinstance(input_value, dict):
      tool_input = input_value
    else:
      try:
          # Attempt to parse 'input' as JSON
          parsed_input = json.loads(input_value)
          if isinstance(parsed_input, dict):
              tool_input = parsed_input
          else:
              tool_input = {"input": input_value}
      except (json.JSONDecodeError, TypeError):
          tool_input = {"input": input_value}


    print("Next Tool Call Args: ", master_agent_input)

    tool_call_id = tool_call.id
    prompt_tokens = response.usage.prompt_tokens
    reply_tokens = response.usage.completion_tokens

    logs_data = {
        "log_id": log_id,
        "thread_id": thread_id,
        "message_id": message_id,
        "agent_name": agent,
        "user_question": user_input,
        "agent_prompt": message,
        "agent_response": {"tool_call": tool_name, "tool_input": tool_input},
        "prompt_token": prompt_tokens,
        "output_token": reply_tokens + prompt_tokens,
        "completion_tokens": reply_tokens,
        "timestamp": datetime.now().isoformat(),
        "planning": (
            (
                {key: plan[key] for key in ["the_plan", "status", "next_step"]}
                if all(key in plan for key in ["the_plan", "status", "next_step"])
                else None
            ),
        ),
    }
    await store_logs(sid, logs_data)

    user_info = user_tokens.get(sid)

    # # to guarantee model always pass file_url
    # if 'file_url' in master_agent_input:
    #   master_agent_input['file_url'] = user_info.get('last_file_url', '')

    tool_output = await call_tool_function(
        tool_name, user_input, master_agent_input, sid, message_id, thread_id
    )
    # print('Tool output - Master Agent return: ', tool_output)

    tool_history = [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": str(master_agent_input),
                    },
                }
            ],
        },
        {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": tool_name,
            "content": str(tool_output),
        },
    ]
    master_agent_input = None

    return tool_name, master_agent_input, tool_call_id, tool_output, tool_history


####### PRECISA FAZER O LOAD DO SYSTEM PROMPT DO CLIENT - DO PROMPT HUB NO MONGO
#######  QUE RECEBE O SID, LOAD A LISTA com PROMPT MAESTRO DO CLIENT na primeira posiçao.

message = [{"role": "system", "content": maestro}]


async def maestro_agent(data_user, sid):
    user_input = data_user["message"]["userInput"]
    thread_id = data_user["thread_id"]
    message_id = data_user["message"]["id"]

    user_info = user_tokens.get(sid)

    ###ALEX, ajustar para termos o histórico de conversa em arquivo local ou mesmo em memória
    # client, db = get_mongo_client('nicodb')
    # history_messages = get_collection(db, 'history_messages')

    # existing_message = history_messages.find_one(
    #   {'userId': user_info['userId'], 'thread_id': thread_id},
    #   {
    #     "session_id": 0,
    #     "thread_id": 0,
    #     "customer_id": 0,
    #     "userId": 0,
    #     "messages.id": 0
    #   }
    # )

    # if existing_message:
    #   message = existing_message['messages']
    # else:
    #   message = [{"role": "system", "content": maestro}]

    message.append(
        {"role": "user", "content": user_input}
    )  # adiciona a mensagem que entrs no histórico. Garante que atualiza o sid (essa chamada como
    # ou sid["conversation_history"].append({"role": "user", "content": user_input})

    last_tool_names = []  # List to track the last few tool names

    while True:
        # Call the message_master_agent function
        tool_name, master_agent_input, tool_call_id, tool_output, tool_history = (
            await run_master_agent(message, user_input, sid, message_id, thread_id)
        )

        # Guarantee tool output is a dictionary
        # tool_output = parse_tool_output(tool_output)

        # print('Type', type(tool_output), '\nFinal tool output', tool_output)

        tool_output = parse_tool_output(tool_output)
        # Check if 'status' is 'success' and 'html_answer' has a value. Brake if it is.
        if tool_output.get("status") == "success" and tool_output.get("html_answer"):
            message.append(
                {"role": "assistant", "content": tool_output.get("html_answer")}
            )
            # store_thread(sid, thread_id, message)
            break

        # Append the latest input and tool output to the message history
        message.extend(
            tool_history
        )  # ou sid["conversation_history"].extend, tool_history já é lista
        message.append(
            {
                "role": "user",
                "content": f"""Take a look our conversation history to craft the best strategy
                                                        to answer my original input"{user_input}". Your next step should be based on last tool output.
                                                        Decide which tool to call next.
                                                        DO NOT CONSIDER THE LANGUAGE OF ORIGINAL INPUT WHEN WRITING FINAL ANSWER""",
            }
        )
        # store_thread(sid, thread_id, message)

        last_tool_names.append(tool_name)

        # Keep only the last 4 tool names in the list
        if len(last_tool_names) > 4:
            last_tool_names.pop(0)

        # Check if the tool_name has been the same for the last 4 iterations
        if len(last_tool_names) == 4 and all(
            name == tool_name for name in last_tool_names
        ):
            print(
                "Tool name has been the same for four consecutive iterations. Breaking the loop."
            )
            break  # Exit the loop if the tool_name has been the same for 4 times in a row

    # Return the last tool_output, whether it was successful or not
    return tool_output


# user_input = 'What is the average monthly sales from march to july?'
# a = maestro_agent(user_input, sid=12, client_id=None, userProfileId=None)
# print(a)

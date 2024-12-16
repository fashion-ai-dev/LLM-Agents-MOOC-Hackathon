from openai import OpenAI
from dotenv import load_dotenv
import os
from platform_hub.prompt_hub import html_agent
import json
from platform_hub.logs import store_logs
import uuid
from build_tools.build_tools import html_tools
from datetime import datetime
from openai_client.connection import OpenAISingleton

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

open_ai = None


async def run_html_answer(message,user_input,master_agent_input,sid, message_id, thread_id):

    model_settings = {
        "model": "gpt-4o",
        "seed": 1000,
        "messages": message,
        "tool_choice": "required",
        "temperature": 0,
        "tools": html_tools,

        }


    # print(message)
    response = OpenAISingleton.get_instance().client.chat.completions.create(**model_settings)
    # print(response)

    tool_call = response.choices[0].message.tool_calls[0]
    # comment = response.choices[0].message.content To be implemented in case a conversation happens instead of a tool call
    print("HTML Tool Call: ", tool_call, "\n\n\n")

    arguments = json.loads(tool_call.function.arguments)
    tool_name = tool_call.function.name
    tool_call_id = tool_call.id

    prompt_tokens = response.usage.prompt_tokens
    reply_tokens = response.usage.completion_tokens
    agent = 'HTML Designer'
    log_id = str(uuid.uuid4())

    logs_data = {
      "log_id": log_id,
      "thread_id": thread_id,
      "message_id": message_id,
      "agent_name": agent,
      "user_question": user_input,
      "agent_response": {'tool_call': tool_name, 'tool_input': arguments},
      "agent_prompt": message,
      "prompt_token": prompt_tokens,
      "output_token": reply_tokens + prompt_tokens,
      "completion_tokens": reply_tokens,
      "timestamp": datetime.now().isoformat(),
    }
    await store_logs(sid, logs_data)

    # Move the import here to avoid circular imports
    from build_tools.trigger_tools import call_tool_function

    tool_output = await call_tool_function(tool_name, user_input, arguments, sid, message_id, thread_id)

    # tool_output['file_url'] = master_agent_input.get('file_url', None)

    print('Tool output', tool_output)  # tool_output = execute_code(arguments['input'],sid)
    # # Parse the chat completion content
    tool_history = [{'role': 'assistant', 'content': None, 'tool_calls': [
      {'id': tool_call_id, 'type': 'function',
       'function': {'name': tool_name, 'arguments': str(arguments)}}
    ]},

                    # Tool result message outputted by the function. Notice content is a JSON string of the tool output in `content`.
                    {'tool_call_id': tool_call_id, 'role': 'tool', 'name': tool_name,
                     'content': str(tool_output)}]

    return arguments, tool_output, tool_call_id, tool_history, tool_name



async def agent_html_designer(user_input, master_agent_input, sid, message_id, thread_id ):


    message = [
        {"role": "system", "content": html_agent},
        {"role": "user", "content": str(master_agent_input)},
    ]

    # print("HTML Designer Prompt: ", message)

    query, output, tool_call_id,tool_history,tool_name = await run_html_answer(message,user_input, master_agent_input, sid, message_id, thread_id )

    # output = parse_tool_output(output)


    # If the loop completes without success, return the last output
    return output


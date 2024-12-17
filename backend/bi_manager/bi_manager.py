# -*- coding: utf-8 -*-
import logging

from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from platform_hub.prompt_hub import bi_manager
from build_tools.build_tools import bi_manager_tools
from platform_hub.logs import store_logs
from datetime import datetime
import uuid
from globals import user_tokens
from openai_client.connection import OpenAISingleton

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

open_ai = None


async def run_bi_manager(message,user_input,master_agent_input,sid, message_id, thread_id):

    log_id = str(uuid.uuid4())
    agent = 'Data Manager'
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

    print("Prompt Bi Manager",message,"\n\n\n")
    model_settings = {
        "model": "ft:gpt-4o-2024-08-06:fashionai:data-manager:AOD4dkU8",#"ft:gpt-4o-2024-08-06:fashionai:bi-manager-dataframe-graphs:ALe1HwXO" #ft:gpt-4o-2024-08-06:personal:graphs-fuzzy:AAhL5Gwd", #ft:gpt-4o-2024-08-06:personal::AAJSmBoO treinado para linha_mixgrupo sobre graphs
        "seed": 100,
        "tools": bi_manager_tools,
        "tool_choice": {"type": "function", "function": {"name": "execute_code"}},
        "parallel_tool_calls": False,
        "messages": message,
        "store": True,
        "metadata": {
            "role": "data_manager",
        },
        "temperature": 0

    }

    try:
      response = OpenAISingleton.get_instance().client.chat.completions.create(**model_settings)
      # print("Response:", response)
    except Exception as e:
      logging.error(f"An error occurred: {e}")
      print(f"An error occurred: {e}")

    tool_call = response.choices[0].message.tool_calls[0]



    arguments = json.loads(tool_call.function.arguments)
    tool_name = tool_call.function.name

    tool_call_id = tool_call.id

    prompt_tokens= response.usage.prompt_tokens
    reply_tokens= response.usage.completion_tokens

    print("Bi Agent Tool Call: ", arguments, "\n\n\n")

    from build_tools.trigger_tools import call_tool_function
    tool_output = await call_tool_function(tool_name, user_input, arguments, sid, message_id, thread_id)

    # user_info = user_tokens.get(sid)

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
      "agent_prompt": message,
      "agent_response": {'tool_call': tool_name, 'tool_input': arguments},
      "code_output": tool_output,
      "prompt_token": prompt_tokens,
      "output_token": reply_tokens + prompt_tokens,
      "completion_tokens": reply_tokens,
      "timestamp": datetime.now().isoformat(),
    }

    await store_logs(sid, logs_data)
    print('Data manager Tool output',tool_output)

    tool_history =  [{'role': 'assistant', 'content': None, 'tool_calls': [
        {'id': tool_call_id, 'type': 'function',
         'function': {'name': tool_name, 'arguments': str(arguments)}}
    ]},

    {'tool_call_id': tool_call_id, 'role': 'tool', 'name': tool_name,
     'content': str(tool_output)}]

    return arguments,tool_output, tool_call_id, tool_history,tool_name


attempts_per_message_id = {}
async def bi_manager_agent(user_input, master_agent_input, sid, message_id, thread_id):

    max_attempts = 3

    # Initialize attempt count for the current message_id if it doesn't exist
    if message_id not in attempts_per_message_id:
      attempts_per_message_id[message_id] = 0

    message = [
        {"role": "system", "content": bi_manager},
        {"role": "user", "content": str(master_agent_input)},
    ]

    while attempts_per_message_id[message_id] < max_attempts:

        print("Bi Agent Attempt: ",attempts_per_message_id[message_id],"\n\n\n")
        # Call the get_sql_query function
        query, output, tool_call_id,tool_history,tool_name = await run_bi_manager(message,user_input, master_agent_input, sid, message_id, thread_id)

        # print('Tool name:',tool_name)

        # print("PYTHON tool output",output,"\n\n\n")
        # Check if the output is a dictionary and has status = success
        # if tool_name == 'answer':
        #   print('Bi Manager: Vou retornar pro Maestro \n')
        #   # Remove message_id from the dictionary once processing is done
        #   del attempts_per_message_id[message_id]
        #   return output

        if output['status'] == 'failure':
          message.extend(tool_history)
          message.append({"role": "user",
                          "content": "There was an error on previous code. Do fix the previous code based on output message of last tool call."})

        elif output['output'] == '':
          message.extend(tool_history)
          message.append({"role": "user",
                          "content": "The code output of last tool call is empty and does not give you the full data needed to answer. Check if escape characters were used poorly and fix it, if code started with a comment sometimes the string makes it a single line comment. Rewrite your code adding the necessary print statement"})
        else:
          return output
        # Increment the attempt counter
        # Increment the attempt counter for the current message_id
        attempts_per_message_id[message_id] += 1

    del attempts_per_message_id[message_id]
    # If the loop completes without success, return the last output
    return output




#####TEST
# message = [{'role': 'system', 'content': '\nYou are very powerful assistant that receives a user input (and a conversation history as background) and writes/run python code to reach a final answer\nwhile using the tool \'execute_code\'.\n\nMake sure to write a well structured code including all necessary steps to reach an answer to user input.\nAdd print statements with head() on each step for debugging. If final output is needed to answer the user, print it.\n\nUse tool \'answer\' to provide a final answer once you are satisfied with the code and data generated.\n\n\nFollow the guidelines listed below when working on your answer:\n- When working with dates, floats and monetary values do format them on a friendly way so it can be used on graphs.\n- Always use chart.js for graphs and save them to a json file. DO NOT use lambda functions on graph code as they are not serializable by the json module.\n- when saving any file ALWAYS use uuid to give a unique name to the file;\n\n\n\n## Special Instruction for sales performance analysis. Pay strict attention to:\n1 - On the python environment where code will run you already have available a function called have \'get_performance_data\'. Function should be used to run analysis on performance classification, sales velocity, total sales per period and so on.Do not import that function to avoid error.\n2 - Function require sales channel as parameter (Options are: "ECOMMERCE", "LOJA FISICA" or "AGREGADO") and returns a data frame. Use "AGREGADO" as default channel if not specified and let the user know abit your decision. Example usage: to get performance data for stores you can write data=get_performance_data("LOJA FISICA").\n3 - When filtering data from get_performance_data you MUST ALWAYS select a valid value fom \'DIAS\' column to avoid duplication. In case user does not specify one use \'DIAS\' = 60 as default and let user know.\n4 - Function will return a df with following data:\n  •\tPRODUTO (int64): product id.\n\t•\tCOR_PRODUTO (int64): product color id.\n\t•\tNUM_FILIAL (int64), CANAL (object): Branch and Channel id. Both point to e-comerce\n\t•\tLINHA_MIX_GRUPO (object): Concatenates product line, mix and group (ex: alfaiataria, tricot).\n\t•\tCOLECAO (object): Collection as INV24 (portuguese for winter 2024).\n\t•\tCOLECAO_ANO (int64): Year of collection as YY.\n\t•\tCOLECAO_EPOCA (object): Season of collection INV or VER (inverno or verão - portuguese).\n\t•\tDIAS (int64): Window of time for performance analysis (7, 14, 21, 30, 60 days). It means first x days after launch, so they make sales data overlap.\n\t•\tVEL_VENDA (float64): Sales velocity (units /day).\n\t•\tPERFORMANCE (float64): Classifier of performance (0 to 4). ALWAYS USE this colum to identify top performing prodcuts.\n\t•\tQTDE_VENDIDA (int64): Total units sold in the time window.\n\t•\tESTOQUE_MEDIO (float64): Average inventory in the time window.\n5 - User may refer to LINHA_MIX_GRUPO as category, line, mix or group as well. To be filtered with values on list retrieved from filter_fuzzy_search(df, search_term, column_name). Function will return a list of matched values.\n6 - Pay special attention on Column names and on filtered values form \'filter_fuzzy_search\' after a print statement. You may realize that user input has a typo and decide to use the values form print statements.\n7 - Be skeptical about empty filtering results. If it happens, do write code again exploring the data.\n8 - PERFORMANCE naming work as follows:\n  - 4: "Best"\n  - 3: "Vende Bem"\n  - 2: "OK"\n  - 1: "Slow bom"\n  - 0: "Sem performance" (sem histórico suficiente)\n- When selecting a season, use the last one by default. Let the user know about this decision.\n\n\n'}, {'role': 'user', 'content': "{'conversation_history': 'Usuário perguntou sobre os produtos best da linha malha.', 'input': 'quais sao os produtos best da linha malha?'}"}]
#
# model_settings = {
#         "model": "ft:gpt-4o-2024-08-06:personal:graphs-fuzzy:AAhL5Gwd", #ft:gpt-4o-2024-08-06:personal::AAJSmBoO treinado para linha_mixgrupo sobre graphs
#         "seed": 100,
#         "tools": python_tools,
#         "tool_choice": "required",
#         "messages": message,
#         "temperature": 0
#
#         }
# print(message)
# response = client.chat.completions.create(**model_settings)
#
# print(response)

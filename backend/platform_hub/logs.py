import uuid
import pandas as pd
from datetime import datetime
import os
from bson import ObjectId
import json
from shared import send_logs, sio
from globals import user_tokens
from jwt.exceptions import ExpiredSignatureError
from bson.objectid import ObjectId


async def store_logs(sid, data):
  user_info = user_tokens.get(sid)

  try:
    data_to_socket = {
      "log_id": data.get('log_id', None),
      "thread_id": data.get('thread_id', None),
      "session_id": sid,
      "message_id": data.get('message_id', None),
      "agent_name": data.get('agent_name', None),
      "user_question": data.get('user_question', None),
      "agent_response": (data.get('agent_response', None)),
      "agent_decision": data.get('agent_response', {}).get('tool_call', None),
      "agent_output": data.get('agent_response', {}).get('tool_input', None),
      "code_output": data.get('code_output', None),
      "agent_prompt": (data.get('agent_prompt', '[]')),
      "agent_prompt_content": data.get('agent_prompt', [{}])[0].get('content', None),
      "conversation_history": data.get('agent_prompt', [])[1:],
      "prompt_token": data.get('prompt_token', None),
      "output_token": data.get('output_token', None),
      "completion_tokens": data.get('completion_tokens', None),
      "timestamp": datetime.now().isoformat(),
      "planning": data.get('planning', None),
    }

    agent_response = data.get('agent_response', None)
    if isinstance(agent_response, dict) and 'tool_input' in agent_response:
      tool_input = agent_response['tool_input']

      # Verifica se o código está no campo 'Code ' ou 'input'
      if isinstance(tool_input, dict):
        if 'Code ' in tool_input:
          data_to_socket['code_snippet'] = tool_input['Code ']
        elif 'code' in tool_input:
          data_to_socket['code_snippet'] = tool_input['code']

    await sio.emit('conversation_logs', data_to_socket, to=sid)

    send_logs_to_mongo(sid, data_to_socket)

  except Exception as e:
    print(f"Erro ao enviar logs: {e}")


def send_logs_to_mongo(sid, data,file_path='logs.json'):
  user_info = user_tokens.get(sid)

  if user_info:
        data['user_info'] = user_info

  try:
        # Load existing logs if file exists, otherwise create an empty list
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                logs = json.load(file)
        else:
            logs = []

        # Append new log data
        logs.append(data)

        # Save logs back to the file
        with open(file_path, 'w') as file:
            json.dump(logs, file, indent=4)

        return data.get('log_id', None)  # Returning log ID or any unique identifier as in Mongo
  except Exception as e:
        print(f"Error writing log to file: {e}")
        return None


def get_logs_from_mongo(user_id, customer_id, thread_id,file_path='logs.json'):
  try:
        # Load existing logs from file
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                logs = json.load(file)
        else:
            logs = []

        # Filter logs based on user_id, customer_id, and thread_id
        filtered_logs = [
            serialize_log(log) for log in logs
            if log.get('user_info', {}).get('userId') == user_id
            and log.get('user_info', {}).get('customer', {}).get('id') == customer_id
            and log.get('thread_id') == thread_id
        ]

        return filtered_logs
  except Exception as e:
        print(f"Error reading logs from file: {e}")
        return []


def serialize_log(log):
  if '_id' in log:
    log['_id'] = str(log['_id'])
  return log


def sanitize_data(data):
  if isinstance(data, dict):
    return {k: sanitize_data(v) for k, v in data.items()}
  elif isinstance(data, list):
    return [sanitize_data(item) for item in data]
  elif isinstance(data, ExpiredSignatureError):
    return str(data)
  elif isinstance(data, Exception):
    return str(data)
  else:
    return data


def send_error_log(sid, error,file_path='error_logs.json'):
    user_info = user_tokens.get(sid)

    # Sanitize user info and error for storage
    sanitized_user_info = sanitize_data(user_info)
    sanitized_error = sanitize_data(error)

    # Prepare the error log entry
    data_to_insert = {
        'user': sanitized_user_info,
        'error': sanitized_error,
        'timestamp': datetime.now().isoformat()
    }

    try:
        # Load existing error logs if file exists, otherwise create an empty list
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                error_logs = json.load(file)
        else:
            error_logs = []

        # Append the new error log
        error_logs.append(data_to_insert)

        # Save updated error logs back to the file
        with open(file_path, 'w') as file:
            json.dump(error_logs, file, indent=4)
    except Exception as e:
        print(f"Error writing error log to file: {e}")

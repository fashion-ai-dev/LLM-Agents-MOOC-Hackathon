
from sql_agent.sql_agent import agent_sql_query
from html_agent.html_agent import agent_html_designer
from bi_manager.bi_manager import bi_manager_agent
from bi_manager.python_env.python_tools_functions import execute_code,send_final_bi_answer
from html_agent.html_tools_functions import send_final_answer


# List of available tools (functions)
  # Add more tools here if necessary

# Create a dictionary mapping tool names to functions
from sql_agent.sql_function import fetch_postgres_data

tool_map = {
    'sql_sales_data_agent': agent_sql_query,
    'html_designer': agent_html_designer,
    'data_manager_agent': bi_manager_agent,
    'run_python_code': execute_code,
    'execute_code': execute_code,
    'answer': send_final_answer,
    'html_output': send_final_answer,
    'test_sql_query': fetch_postgres_data


    # Add more tools/functions here if necessary
}


async def call_tool_function(tool_name, user_input, input, sid, message_id, thread_id, tool_map=tool_map):
    # Retrieve the function from the dictionary
    tool_function = tool_map.get(tool_name)

    # print("Calling from trigger:", tool_name)
    if tool_function:
        # Call the function with the provided arguments
        return await tool_function(user_input, input, sid, message_id, thread_id)
    else:
        raise ValueError(f"Tool '{tool_name}' is not available in the master_tools list.")

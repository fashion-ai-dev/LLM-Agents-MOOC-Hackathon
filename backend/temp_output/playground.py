import contextlib
import io
import json
import os
import tempfile

from sql_agent.sql_function import fetch_postgres_data


def execute_code(user_input, code_dict, sid, message_id, thread_id):
    """
    Runs the provided string as Python code, making `fetch_data` available in the environment.
    Captures print statements and stores generated files in a temp folder.

    Parameters:
    code_dict (dict): A dictionary containing the Python code to be executed.

    Returns:
    result (dict): A dictionary with execution details including status, code executed, output, and file path.
    """
    code_string = code_dict.get('code', '')
    
    print("Code",code_string)
    
    # Create a temporary directory in the script's folder
    temp_folder_path = os.path.join(os.getcwd(), 'temp_output')
    os.makedirs(temp_folder_path, exist_ok=True)

    # Capture the print output
    output = ""
    try:
        environment = {
            "fetch_postgres_data": fetch_postgres_data,
            "os": os,
            "tempfile": tempfile,
            "temp_folder_path": temp_folder_path
        }
        
        # Redirect stdout to capture print statements
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            exec(code_string, environment)
            output = buf.getvalue()

        status = "success"
    except Exception as e:
        output += f"An error occurred: {e}\n"
        status = "failure"

    # Create the result dictionary
    result = {
        "status": status,
        "code_executed": code_string,
        "output": output,
        "file_url": f"file://{temp_folder_path}" if status == "success" else None
    }
    print("Result", result)
    return result


code_dict = '{"code":"# SQL query to get the total daily revenue in September, including the date and daily revenue\\nquery = \'\'\'\\nSELECT \\"creationDate\\"::DATE AS date, SUM(first_orders.\\"total_Items_value\\") AS daily_revenue\\nFROM (\\n    SELECT DISTINCT ON (\\"orderId\\") \\"orderId\\", \\"total_Items_value\\", \\"creationDate\\"\\n    FROM sales_history\\n    WHERE EXTRACT(YEAR FROM \\"creationDate\\") = EXTRACT(YEAR FROM CURRENT_DATE)\\n    AND EXTRACT(MONTH FROM \\"creationDate\\") = 9\\n    ORDER BY \\"orderId\\", \\"creationDate\\"\\n) AS first_orders\\nGROUP BY date\\nORDER BY date\\n\'\'\'\\n\\n# Function to fetch data from the database\\ndf_daily_revenue_sep = fetch_postgres_data(query)\\n\\n# Print the first 5 rows of the dataframe for debugging\\nprint(df_daily_revenue_sep.head(5))\\n\\n# Save the dataframe to a CSV file\\ndf_daily_revenue_sep.to_csv(\'daily_revenue_sep.csv\', index=False)"}'
code_dict = json.loads(code_dict)
a = execute_code(0, code_dict, 0, 0, 0)
print(a)

import contextlib
import shutil
import sys
import textwrap
import types

from dotenv import load_dotenv
from bi_manager.python_env.imports import install_package, clients_environments
import os
import io
from contextlib import redirect_stdout
from bi_manager.python_env.imports import prepare_environment
from globals import user_tokens, customer_environments
import json
from sql_agent.sql_function import fetch_postgres_data
import io
import tempfile
import os

load_dotenv()

port = os.getenv('PORT')


# async def execute_code(user_input, code, sid, message_id, thread_id):
#     """
#     Execute a string of Python code using exec() within a client-specific working directory
#     and upload files to S3 if a directory is provided.

#     :param client: The identifier for the client.
#     :param code: The code to execute.
#     :param s3_directory: The S3 directory to upload files after execution.
#     :return: Result message indicating the outcome of the code execution.
#     """

    

#     # Query to filter documents where customer_id=2
#     user_info = user_tokens.get(sid)

#     # print("user info com sucesso \n", user_info)

#     functions = [] # Only retrieve the 'functions' field

#     # Unpack the 'functions' list and pass it to prepare_environment
#     # environment = prepare_environment(1, functions, sid)
#     # optimize, so we do not have to load env in every call.

#     # print("enviroment com sucesso \n",environment)

#     # Set up the client-specific working directory
#     current_directory = os.getcwd()
#     working_directory = os.path.join(
#         current_directory, f"tmp/local_dir/1")
#     os.makedirs(working_directory, exist_ok=True)

#     original_directory = os.getcwd()  # Save the current directory

#     # Assuming `code` can either be a dictionary or a JSON string
#     if isinstance(code, str):
#       # Try to load the string as JSON
#       code = json.loads(code)

#     customer_environments = {}

#     code_str = str(
#         code['code']) 
    
   

#     def run_code():
#         f = io.StringIO()
#         try:
#             with redirect_stdout(f):
                
#                 print("vou tentar")# Add sid directly to the global environment
#                 environment = {"fetch_data": fetch_postgres_data}
#                 # environment['customer_environments'] = customer_environments
#                 # environment.update(customer_environments)
#                 # Ensure the user's code is properly indented
#                 indented_code = textwrap.indent(code_str, '  ')
#                 # Wrap the user's code in a function to create a new scope
#                 wrapped_code = f"""

# def execute_user_code():
# {indented_code}

# execute_user_code()
#         """
                
#                 exec(wrapped_code, environment)
#         except Exception as e:
#             return f"Error: {str(e)}"
#         return f.getvalue()

#     try:
#         # Change to the client-specific working directory
#         os.chdir(working_directory)

#         # print('Estou aqui. Code: \n',code,'\nEnviroment:\n',environment)
#         # Execute the code using exec() with the client's environment
#         print("vou rodar codigo: ",code_str)
#         output = run_code()
#         print("output: ", ou)

#         # Check if any files exist in the working directory and upload them to S3
#         files_uploaded = False
#         s3_file_path = None
#         for root, dirs, files in os.walk(working_directory):
#             if files:  # Only proceed if there are files to upload
#                 files_uploaded = True
#                 for file in files:
#                     local_file_path = os.path.join(root, file)
#                     s3_file_path = upload_to_s3("1", local_file_path, file)
#                     if s3_file_path:
#                         # Delete the local file after successful upload
#                         os.remove(local_file_path)

#         if files_uploaded:

#             return {"status": "success", "code_executed": code['code'], "output": output, "file_url": s3_file_path}
#         elif output.startswith("Error:"):
#             return {"status": "error", "code_executed": code['code'], "output": "Previous code generated the error below. Make sure to add debugging statements when fixing it.\n "+output, "file_url": None}
#         else:
#             return {"status": "success", "code_executed": code['code'], "output": output, "file_url": None}

#     except ModuleNotFoundError as e:
#         # Handle missing module error and attempt to install it
#         missing_module = str(e).split("'")[1]
#         install_message = install_package(missing_module)
#         if "successfully" in install_message:
#             # Re-run the code after installing the missing module
#             try:
#                 output = run_code()
#                 # Repeat the process for file uploading
#                 files_uploaded = False
#                 s3_file_path = None
#                 for root, dirs, files in os.walk(working_directory):
#                     if files:  # Only proceed if there are files to upload
#                         files_uploaded = True
#                         for file in files:
#                             local_file_path = os.path.join(root, file)
#                             s3_file_path = upload_to_s3(
#                                 1, local_file_path, file)
#                             if s3_file_path:
#                                 # Delete the local file after successful upload
#                                 os.remove(local_file_path)

#                 if files_uploaded:
#                     return {"status": "success", "code_executed": code, "output": output, "file_url": s3_file_path}
#                 else:
#                     return {"status": "success", "code_executed": code, "output": output, "file_url": None}
#             except Exception as e:
#                 return {"status": "error", "code_executed": code, "output": str(e), "file_url": None}
#         else:
#             return {"status": "error", "output": install_message, "file_url": None}

#     except Exception as e:
#         return {"status": "error", "output": str(e), "file_url": None}

#     finally:
#         # Restore the original directory after execution
#         os.chdir(original_directory)


async def send_final_bi_answer(user_input, input, sid, message_id, thread_id):

    return input
#
# code_A = """
# # Call the function to get the string
# output = bq_data()
#
#
# print(f"Data {output.head()}")
# """
# #
# code_B = """
# # Print the output 3 times
# for a in range(3):
#     print(a)
# """
#
# result = execute_code('Client_A', code_A)
# print(result)
# result = execute_code('Client_A', code_B)
# print(result)

######### SEARCH STRING COLUMNS#######

# Persistent environment dictionary to keep variables between runs
environment = {
    "fetch_postgres_data": fetch_postgres_data,
    "os": os,
    "tempfile": tempfile
}

async def execute_code(user_input, code_dict, sid, message_id, thread_id):
    """
    Runs the provided string as Python code, making `fetch_postgres_data` available in the environment.
    Captures print statements and stores generated files in a temp folder.

    Parameters:
    code_dict (dict): A dictionary containing the Python code to be executed.

    Returns:
    result (dict): A dictionary with execution details including status, code executed, output, and file path.
    """
    code_string = code_dict.get('code', '')
    
    # Create directories for file management
    script_folder = os.getcwd()
    python_env_folder_path = os.path.join(script_folder, 'python_env')
    ui_files_folder_path = os.path.join(script_folder, 'public')
    os.makedirs(python_env_folder_path, exist_ok=True)
    os.makedirs(ui_files_folder_path, exist_ok=True)

    # Capture the print output
    output = ""
    status = "failure"
    file_path = ""
    file_paths = []
    original_cwd = os.getcwd()  # Save the original current working directory

    try:
        # Update the environment with additional paths
        environment.update({
            "python_env_folder_path": python_env_folder_path,
            "ui_files_folder_path": ui_files_folder_path
        })
        
        # Redirect stdout to capture print statements
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            # Change current working directory to python_env_folder_path to ensure files are saved there
            os.chdir(python_env_folder_path)
            
            exec(code_string, environment)
            output = buf.getvalue()

        # Check if any file was created in the python_env folder
        created_files = []
        for item in os.listdir(python_env_folder_path):
            item_path = os.path.join(python_env_folder_path, item)
            if os.path.isfile(item_path):
                created_files.append(item_path)
                
        # Move created files to UI_files folder, replacing if it already exists
        for file_path in created_files:
            destination_path = os.path.join(ui_files_folder_path, os.path.basename(file_path))

            if os.path.exists(destination_path):
                print("# Overwrite the existing file")
                os.remove(destination_path)

            shutil.move(file_path, destination_path)
            file_paths.append(f"http://localhost:{port}/public/{os.path.basename(file_path)}")

        # Update status to success if no exception occurred
        status = "success"
        
    except Exception as e:
        output += f"Previous code generated the error below. Make sure to add debugging statements when fixing it: {e}\n"
    finally:
        # Always revert to the original working directory
        os.chdir(original_cwd)

    # Create the result dictionary
    result = {
        "status": status,
        "code_executed": code_string,
        "output": output,
        "file_paths": file_paths if status == "success" else None
    }
    return result
        


# code_dict = '{"code":"# SQL query to get the total daily revenue in September, including the date and daily revenue\\nquery = \'\'\'\\nSELECT \\"creationDate\\"::DATE AS date, SUM(first_orders.\\"total_Items_value\\") AS daily_revenue\\nFROM (\\n    SELECT DISTINCT ON (\\"orderId\\") \\"orderId\\", \\"total_Items_value\\", \\"creationDate\\"\\n    FROM sales_history\\n    WHERE EXTRACT(YEAR FROM \\"creationDate\\") = EXTRACT(YEAR FROM CURRENT_DATE)\\n    AND EXTRACT(MONTH FROM \\"creationDate\\") = 9\\n    ORDER BY \\"orderId\\", \\"creationDate\\"\\n) AS first_orders\\nGROUP BY date\\nORDER BY date\\n\'\'\'\\n\\n# Function to fetch data from the database\\ndf_daily_revenue_sep = fetch_postgres_data(query)\\n\\n# Print the first 5 rows of the dataframe for debugging\\nprint(df_daily_revenue_sep.head(5))\\n\\n# Save the dataframe to a CSV file\\ndf_daily_revenue_sep.to_csv(\'daily_revenue_sep.csv\', index=False)"}'
# code_dict = json.loads(code_dict)
# a = execute_code(0, code_dict, 0, 0, 0)
# print(a)
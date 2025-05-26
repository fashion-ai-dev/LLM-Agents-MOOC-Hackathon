######## Maestro Tools
plan_scratchpad= {
    "type": "function",
    "function": {
        "name": "plan_scratchpad",
        "description": "Use this tool to document and update the step-by-step plan for using other tools to reach a final answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "the_plan": {
                    "type": "string",
                    "description": "For every new user input, write a short description of what the expected answere should look like and how you will use the other tools to reach a final answer on a step-by-step approach."
                                   "While an answer is not provided do not update the plan, unless really necessary."
                                   "On a conversation history, a new user message equals a new plan focused on the last message.",
                },
                "status": {
                    "type": "string",
                    "description": "quick summary of what has been accomplished so far. If any previous step was not completed successully make sure to poit out that it is pending."
                },
                "next_step": {
                    "type": "string",
                    "description": "Describe the next step you are going to take to move towards the answer. Are you moving forward with the plan and calling a next task or do you need to fix any previous steps?"
                },
                "next_tool": {
                    "type": "string",
                    "enum": ["sql_sales_data_agent", "data_manager_agent", "html_designer"],
                    "description": "Specify the name of the next tool to be called."
                },
                "next_tool_arguments": {
                    "type": "string",
                    "description": "Write the tool call with required arguments and values for the next tool (e.g., required key values)."
                }
            },
            "required": ["the_plan", "status", "next_step", "next_tool", "next_tool_arguments"],
            "additionalProperties": False
        }
    }
}

sql_sales_data_agent = {
    "type": "function",
    "function": {

    "name": "sql_sales_data_agent",
    "description": """Use this LLM Agent to retrieve Sales History Data. It ha access to the SQL DB that is needed to fetch sales history data.
    This tool does not have access to catalog data.
    Input should be a human text (not code) explaining to a junior data engineer what data you need and output will be a dataframe.
    Do not ask it to format numbers, transform or save data to files.
    
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Description of the data you need to retrieve from sales history.",
            },
        },
        "required": ["input"],
        "additionalProperties": False,
    }
}}

data_manager_agent = {
    "type": "function",
    "function": {

    "name": "data_manager_agent",
    "description": """It is a business intelligence manager that can write and run python code to transform or analyse data.
      It shares the same python env as the sql_sales_data_agent, so you can share the name of any dataframe or files that contains data that should be used.
      Do write in ENGLISH when using this tool and be very prescriptive on how it should access the data. Assume it is a very junior agent that needs clear instructions.
      """,
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Pass a single JSON-formatted string containing three top‑level keys:\n"
                               "1. briefing – concise statement of WHAT to do;\n"
                               "2. data_sources – object describing each DataFrame/file (columns, description, keys);\n"
                               "3. guide – step‑by‑step HOW to use the data_sources.\n"
                               "Example:\n"
                               "{\n"
                               "  \"briefing\": \"Create a customer cluster for high‑value users\",\n"
                               "  \"data_sources\": {\n"
                               "     \"df_users\": {\n"
                               "        \"columns\": {\"id\": \"User ID\", \"score\": \"Relevance score\"},\n"
                               "        \"description\": \"Users matching fashion concept\",\n"
                               "        \"keys\": [\"id\"]\n"
                               "     },\n"
                               "     \"df_orders\": {\n"
                               "        \"columns\": {\"user_id\": \"User ID\", \"total\": \"Order value\"},\n"
                               "        \"description\": \"Orders list\",\n"
                               "        \"keys\": [\"user_id\"]\n"
                               "     }\n"
                               "  },\n"
                               "  \"guide\": \"Join df_users.id with df_orders.user_id; ...\"\n"
                               "}"
            }
        },
        "required": ["input"],
        "additionalProperties": False,
    }
}}

style_agent = {
    "type": "function",
    "function": {

    "name": "style_agent",
    "description": """An agent that receives a fashion concept from the user query and returns a cluster of products or 
    customers that match the query.
      """,
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
              "type": "string",
              "description": "A query with fashion concept, looks, occasions, etc that comes fom the user input."
                      ""
            },
        },
        "required": ["input"],
        "additionalProperties": False,
    }
}}

scheduler = {
    "type": "function",
    "function": {

    "name": "scheduler",
    "description": """Python script that will run continuously to update output files.
      """,
    "parameters": {
        "type": "object",
        "properties": {
            "script": {
              "type": "string",
              "description": "Write a python script that can be used to update the output files when run. "
                             "By default set a frequency of once per month, unless user specifies another frequency."
                             "Make sure to use the exact same code successfully used by tools and files paths."
                      ""
            },
        },
        "required": ["input"],
        "additionalProperties": False,
    }
}}

html_designer = {
    "type": "function",
    "function": {

    "name": "html_designer",
    "description": """Use this tool to write your final answer in html format. During a conversation history each answer must be written for the last user input.
        If user expects a file to be downloaded, consider final output will have a hyperlink on some word of your final text.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": (
                        "Pass a single JSON-formatted string with two keys:\n"
                        "1. feedback_message – explanation of how clusters were created (or why not);\n"
                        "2. files – array of URL strings pointing to generated files.\n"
                        "Example:\n"
                        "{\n"
                        "  \"feedback_message\": \"Clusters generated using k-means …\",\n"
                        "  \"files\": [\n"
                        "    \"https://example.com/cluster_products.csv\",\n"
                        "    \"https://example.com/cluster_users.csv\"\n"
                        "  ]\n"
                        "}"
                    )
                }
            },
            "required": ["input"],
            "additionalProperties": False,
        }
}}




master_tools = [html_designer,plan_scratchpad,sql_sales_data_agent,data_manager_agent,style_agent]




########################### Python Tool##################




run_python_code = {
    "type": "function",
    "function": {
        "name": "execute_code",
        "description": """Use this tool to run your python code""",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": """Write your python code to execute instructions received from user. 
                    Make sure to use data informed by user. Pay strict attention to name of variables o files and reuse them if needed."""
                },
            },
            "required": ["code"],
            "additionalProperties": False,
        }
    }
}

answer = {
    "type": "function",
    "function": {
        "name": "answer",
        "description": "Use this tool to share your final answer",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": """Return 'success' if the final code runs properly and answers the question.
                                      Return 'error' if the final code has issues.
                                      Return 'no code' if you did not generate any code and want to answer."""},
                "point_of_attention": {
                    "type": "string",
                    "description": """Analyze the code output from execute_code and provide feedback on issues like default values, abbreviations, or typos in column or value names if they differ from user input. Do NOT return anything if no differences show up.""",
                },
                "output": {
                    "type": "string",
                    "description": """Provide the best answer to the user based on code results. When user asks for data, you should use one of these three options:\
                                      1. Write a table or list with key output values (preferred for 10 or fewer results); \
                                      2. Write a couple of output values in the answer and share the output file (preferred for more than 10 results); \
                                      3. Share the file created if the user requested a file or graph.""",
                },
                "file_url": {
                    "type": "string",
                    "description": "ALWAYS pass the file URL you receive under file_url from execute_code, or an empty string if no file.",
                },
            },
            "required": ["status", "output", "point_of_attention", "file_url"],
            "additionalProperties": False,
        }
    }
}


bi_manager_tools =[run_python_code]
style_agent_tools =[run_python_code]

########################### HTMl TOOLS###########################
html_output = {
    "type": "function",
    "function": {

    "name": "html_output",
    "description": """Use this tool to output your final html with an answer to the original question.""",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Pass success if you are able to return a fina html with answer. Pass failure with an explanation in case you cannot generate a html response.",
            },
            "html_answer": {
                "type": "string",
                "description": "Write the final response in a HTML format following the guidelines and examples you were given. Please do not use html tags inside the script. Do guarantee that html_answer is in the same language as the original_question, translate answer if needed.",
            },
            "file_url": {
                "type": "string",
                "description": "pass the file path (not necessarily a url) received from user under file_url. If no file is present return''.",
            },
        },
        "required": ["input","html_answer","file_url"],
        "additionalProperties": False,
    }
}}

html_tools=[html_output]


##### SQL AGENT

sql_agent_tools= [run_python_code]

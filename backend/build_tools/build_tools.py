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
    Do write in ENGLISH when using this tool.
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
      Do write in ENGLISH when using this tool.
      """,
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
              "type": "string",
              "description": "Describe what you need the tool to do (ex: generate a graph..., save data to a csv..., etc).\n  In case it needs to use a specific data source, make sure you mention the name of the df, file path as well as ALL columns names, so data_manager_agent can access them correctly."
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
                "description": """Your input to the hmtl designer should be a plain text with sections below:
                - the original user question/input to be answered. Do not change languages;

                - Your desired answer that will be formatted into html. Pay strict attention to the following rules:
                1 - Do not share files unless asked by the user.
                2 - If answer has a graph, write your answer adding '<div class="chart-content"></div>' in the place of text the graph should be added.
                3 - Translate the final answer to the same language as 'original_question' in case it is not..
                4 - You may adjust the text received from Bi_manager to make it human friendly (avoid using math characters or passing code snipets) optmize the final answer structure.
                5 - Be helpful and insightful, offer the possibility of variations of the data when it makes sense.

                - file_url: URL to any file supporting the answer. Pass '' if no file was created.
                """
            },

        },
        "required": ["input"],
        "additionalProperties": False,
    }
}}




master_tools = [html_designer,plan_scratchpad,sql_sales_data_agent,data_manager_agent]




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
                    Make sure to use data infromed by user. Pay strict attention to name of variables o files and reuse them if needed."""
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


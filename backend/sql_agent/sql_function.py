import re
import pandas as pd
import duckdb
import os


### SQL AGENT MODEL HAS BEEN TRAINED TO USE FUNCTION BELOW
### Production env should serve DB from Postgres.
### Function adjusted to demo/ local env.
   
def fetch_postgres_data(sql_code, file_name='sales_history_dummy_data.csv'):
    """
    Executes a SQL query on a CSV file using DuckDB.

    Parameters:
    sql_code (str): The SQL query to execute.
    file_name (str): The name of the CSV file containing the data.

    Returns:
    pd.DataFrame: The result of the query as a DataFrame.
    """
    # Construct the file path relative to the script location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)

    try:
        # Load the CSV file into a DuckDB connection
        conn = duckdb.connect(':memory:')
        conn.execute(f"CREATE TABLE sales_history AS SELECT * FROM read_csv_auto('{file_path}')")

        # Adjust PostgreSQL-specific constructs to DuckDB-compatible syntax
        # Wrap column names in double quotes to handle potential case sensitivity
        sql_code = re.sub(r'"(\w+)"', r'"\1"', sql_code)
        
        # Replace PostgreSQL date functions with DuckDB equivalents
        sql_code = re.sub(
            r"TO_CHAR\(([^,]+),\s*'DD-MM-YY'\)", 
            r"strftime(\1, '%d-%m-%y')", 
            sql_code
        )
        
        # Replace EXTRACT functions
        sql_code = re.sub(
            r'EXTRACT\(YEAR FROM\s+([^)]+)\)', 
            r'YEAR(\1)', 
            sql_code
        )
        
        sql_code = re.sub(
            r'EXTRACT\(MONTH FROM\s+([^)]+)\)', 
            r'MONTH(\1)', 
            sql_code
        )
        
        # Replace CURRENT_DATE with current_date
        sql_code = sql_code.replace('CURRENT_DATE', 'current_date')

        # Debug: Print the adjusted query
        print("Adjusted SQL Query:")
        print(sql_code)

        # Execute the SQL query
        query_result = conn.execute(sql_code).df()

        # Ensure all date columns are in ISO format for JSON serialization
        for col in query_result.columns:
            if pd.api.types.is_datetime64_any_dtype(query_result[col]):
                query_result[col] = query_result[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

        return query_result
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error loading CSV file: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error executing SQL query: {str(e)}")

#Test function

# query = '''
# SELECT TO_CHAR("creationDate", 'DD-MM-YY') AS date, SUM(first_orders."total_Items_value") AS revenue
# FROM (
#     SELECT DISTINCT ON ("orderId") "orderId", "total_Items_value", "creationDate"
#     FROM sales_history
#     WHERE EXTRACT(YEAR FROM "creationDate") = EXTRACT(YEAR FROM CURRENT_DATE)
#     AND EXTRACT(MONTH FROM "creationDate") = 9
#     ORDER BY "orderId", "creationDate"
# ) AS first_orders
# GROUP BY date
# ORDER BY date
# '''

# result = fetch_postgres_data(query)
# print(result)
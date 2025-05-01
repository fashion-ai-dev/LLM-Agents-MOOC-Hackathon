import re
import pandas as pd
# import duckdb
import os
import requests


def fetch_postgres_data(sql_code):
    import urllib.parse

    base_url = "http://147.79.110.30:8080/api/v1/products/query"
    #gerar token em: http://147.79.110.30:8080/docs#/Auth/AuthController_login
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjMsInJvbGUiOnsiaWQiOjMsIm5hbWUiOiJBZG1pbiIsIl9fZW50aXR5IjoiUm9sZUVudGl0eSJ9LCJzZXNzaW9uSWQiOjEwMDA4LCJjdXN0b21lciI6eyJpZCI6MTEsInB1YmxpY0lkIjoiZmMyMDRlNjctZDZkOS00NWZjLTlmZGUtMDZmMGNjZWU3MDcyIiwibmFtZSI6ImRlbW8iLCJwbGF0Zm9ybSI6IlZURVgiLCJ1cmwiOiIiLCJsYW5ndWFnZSI6IlBULUJSIiwic2VvTGFuZ3VhZ2UiOiJQVC1CUiIsImFkZGl0aW9uYWxTZW9MYW5ndWFnZSI6W10sImNhdGVnb3JpZXMiOm51bGwsImZldGNoZWRQcm9kdWN0cyI6ZmFsc2UsInRheG9ub215VmVyc2lvbiI6IjQiLCJ2aXNpb25DYXRlZ29yaWVzQXZhaWxhYmxlIjpudWxsLCJjb2xvcnMiOm51bGwsImNvbGxlY3Rpb25zIjpudWxsLCJmaWx0ZXJDb2xvcnMiOm51bGwsImNvbG9yRmFtaWxpZXMiOm51bGwsImJyYW5kcyI6bnVsbCwic2l6ZXMiOm51bGwsImxvZ29VcmwiOm51bGwsInZ0ZXhBcHBLZXkiOiJ2dGV4YXBwa2V5LWZhcm1sYXRhbS1IRkxPWkwiLCJ2dGV4QXBwVG9rZW4iOiJCTVZHWkZIVFlSQUpYTkVIQVhESVZXQkhHQ0paSlRVS05FV0ZDTVZKSUtFUENGUFJLUldIVEFYTFhES05JTUlXUElBRVpMUVVIUUdHSkdHTEdSRE1RWkdSWlZIV1BYUE5KRU9YRFJXRE1GWkpBWlVKS0dCWUROWUZPWkNYTlhMRSIsInZ0ZXhVcmwiOiJodHRwczovL2Zhcm1sYXRhbS5teXZ0ZXguY29tIiwidnRleEFmZmlsaWF0ZVVybCI6bnVsbCwidnRleEFmZmlsaWF0ZUlkIjoiRkZGIiwidnRleFNhbGVzQ2hhbm5lbCI6IjEiLCJmcmVlbWl1bSI6dHJ1ZSwiZnJlZW1pdW1GZXRjaGVkUHJvZHVjdHMiOnRydWUsImZyZWVtaXVtTWF4UHJvZHVjdHNQZXJDYXRlZ29yeSI6NSwiZnJlZW1pdW1NYXhUb3RhbFByb2R1Y3RzIjo0MCwibmVlZFVwZGF0ZUNhdGVnb3J5TmFtZSI6dHJ1ZSwiZmV0Y2hlZFNhbGVzIjpmYWxzZSwibWV0YV91c2VyX3Rva2VuIjpudWxsLCJtZXRhX3BhZ2VfaWQiOm51bGwsIm1ldGFfYWRfYWNjb3VudF9pZCI6bnVsbCwibWV0YV9idXNpbmVzc19pZCI6bnVsbCwibWV0YV9jYXRhbG9nX2lkIjpudWxsLCJzaW1pbGFyaXR5U2VhcmNoQ291bnQiOm51bGwsImh1YnNwb3RUb2tlbiI6IiIsInZpc2lvbkF1dG9SdW4iOnRydWUsInZpc2lvbkxhc3RTdWJtaXNzaW9uIjoiMjAyNS0wNC0zMFQyMDo1MToxMi4wMTBaIiwidnRleE5vdGlmaWNhdGlvbnNDb3VudCI6MH0sImlhdCI6MTc0NjExNjMxMiwiZXhwIjoxNzQ2NTQ4MzEyfQ.kjEqM6kbzxyPNpY_IllyfqSHpyG8DANw0GQwtCYLoj8"

    encoded_query = urllib.parse.quote(sql_code)
    url = f"{base_url}?query={encoded_query}"

    headers = {
        "accept": "*/*",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            return pd.DataFrame(data)
        except ValueError as e:
            raise ValueError(f"Error parsing JSON response: {str(e)}")
    else:
        raise RuntimeError(f"Error {response.status_code}: {response.text}")


### SQL AGENT MODEL HAS BEEN TRAINED TO USE FUNCTION BELOW
### Production env should serve DB from Postgres.
### Function adjusted to demo/ local env.
   
# def fetch_postgres_data(sql_code, file_name='sales_history_dummy_data.csv'):
#     """
#     Executes a SQL query on a CSV file using DuckDB.
#
#     Parameters:
#     sql_code (str): The SQL query to execute.
#     file_name (str): The name of the CSV file containing the data.
#
#     Returns:
#     pd.DataFrame: The result of the query as a DataFrame.
#     """
#     # Construct the file path relative to the script location
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     file_path = os.path.join(current_dir, file_name)
#
#     try:
#         # Load the CSV file into a DuckDB connection
#         conn = duckdb.connect(':memory:')
#         conn.execute(f"CREATE TABLE sales_history AS SELECT * FROM read_csv_auto('{file_path}')")
#
#         # Adjust PostgreSQL-specific constructs to DuckDB-compatible syntax
#         # Wrap column names in double quotes to handle potential case sensitivity
#         sql_code = re.sub(r'"(\w+)"', r'"\1"', sql_code)
#
#         # Replace PostgreSQL date functions with DuckDB equivalents
#         sql_code = re.sub(
#             r"TO_CHAR\(([^,]+),\s*'DD-MM-YY'\)",
#             r"strftime(\1, '%d-%m-%y')",
#             sql_code
#         )
#
#         # Replace EXTRACT functions
#         sql_code = re.sub(
#             r'EXTRACT\(YEAR FROM\s+([^)]+)\)',
#             r'YEAR(\1)',
#             sql_code
#         )
#
#         sql_code = re.sub(
#             r'EXTRACT\(MONTH FROM\s+([^)]+)\)',
#             r'MONTH(\1)',
#             sql_code
#         )
#
#         # Replace CURRENT_DATE with current_date
#         sql_code = sql_code.replace('CURRENT_DATE', 'current_date')
#
#         # Debug: Print the adjusted query
#         print("Adjusted SQL Query:")
#         print(sql_code)
#
#         # Execute the SQL query
#         query_result = conn.execute(sql_code).df()
#
#         # Ensure all date columns are in ISO format for JSON serialization
#         for col in query_result.columns:
#             if pd.api.types.is_datetime64_any_dtype(query_result[col]):
#                 query_result[col] = query_result[col].dt.strftime('%Y-%m-%dT%H:%M:%S')
#
#         return query_result
#     except FileNotFoundError as e:
#         raise FileNotFoundError(f"Error loading CSV file: {str(e)}")
#     except Exception as e:
#         raise RuntimeError(f"Error executing SQL query: {str(e)}")

#Test function

query = '''
SELECT TO_CHAR("creationDate", 'DD-MM-YY') AS date, SUM(first_orders."total_Items_value") AS revenue
FROM (
    SELECT DISTINCT ON ("orderId") "orderId", "total_Items_value", "creationDate"
    FROM sales_history
    WHERE EXTRACT(YEAR FROM "creationDate") = 2024
    AND EXTRACT(MONTH FROM "creationDate") = 9
    ORDER BY "orderId", "creationDate"
) AS first_orders
GROUP BY date
ORDER BY date
'''

result = fetch_postgres_data(query)
print(result)
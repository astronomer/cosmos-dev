import os

dbt_exec_path = "dbt"
dbt_root_directory = '/usr/local/airflow/dags/dbt'

if os.getenv("ENVIRONMENT", "DEV") == "PROD":
    sources = [
        {
            "conn_type": "snowflake",
            "conn_id": "snowflake_default",
            "schema": "chronek",
            "dbt_executable_path": dbt_exec_path
        },
        {
            "conn_type": "bigquery",
            "conn_id": "bigquery_default",
            "schema": "cosmos_testing",
            "dbt_executable_path": dbt_exec_path
        },
        {
            "conn_type": "postgres",
            "conn_id": "postgres_default",
            "schema": "public",
            "dbt_executable_path": dbt_exec_path
        },
        {
            "conn_type": "redshift",
            "conn_id": "redshift_default",
            "schema": "public",
            "dbt_executable_path": dbt_exec_path
        },
        {
            "conn_type": "databricks",
            "conn_id": "databricks_default",
            "schema": "cosmos",
            "dbt_executable_path": dbt_exec_path
        },
    ]
else:
    sources = [
        {"conn_type": "postgres", "conn_id": "airflow_db", "schema": "public", "dbt_executable_path": dbt_exec_path}
    ]

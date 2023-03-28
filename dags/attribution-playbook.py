"""
## Attribution Playbook DAG
[Attribution Playbook](https://github.com/dbt-labs/attribution-playbook) is a working dbt project demonstrating how to
model customer attribution. This dbt project originates from dbt labs as an example project with dummy data to
demonstrate a working dbt core project. This DAG uses the cosmos dbt parser to generate a DAG from the dbt project
folder

"""
import os

from airflow.datasets import Dataset
from pendulum import datetime

from cosmos.providers.dbt.dag import DbtDag


DBT_ROOT_PATH = os.getenv("DBT_ROOT_PATH", "/usr/local/airflow/dags/dbt")
DBT_EXECUTABLE_PATH = os.getenv("DBT_EXECUTABLE_PATH", "/usr/local/airflow/dbt_venv/bin/dbt")


attribution_playbook = DbtDag(
    dbt_root_path=DBT_ROOT_PATH,
    dbt_project_name="attribution-playbook",
    conn_id="airflow_db",
    dbt_args={"schema": "public", "dbt_executable_path": DBT_EXECUTABLE_PATH},
    dag_id="attribution-playbook",
    start_date=datetime(2022, 11, 27),
    schedule=[Dataset("SEED://ATTRIBUTION_PLAYBOOK")],
    doc_md=__doc__,
    catchup=False,
    default_args={"owner": "02-TRANSFORM"},
)

attribution_playbook
"""
## Extract DAG

This DAG is used to illustrate setting an upstream dependency from the dbt DAGs. Notice the `outlets` parameter on the
`DbtSeedOperator` objects are creating
[Datasets](https://airflow.apache.org/docs/apache-airflow/stable/concepts/datasets.html) these are used in the
`schedule` parameter of the dbt DAGs (`attribution-playbook`, `jaffle_shop`, `mrr-playbook`).

We're using the dbt seed command here to populate the database for the purpose of this demo. Normally an extract DAG
would be ingesting data from various sources (i.e. sftp, blob like s3 or gcs, http endpoint, database, etc.)

"""
import os

from airflow import DAG
from airflow.datasets import Dataset
from airflow.utils.task_group import TaskGroup
from pendulum import datetime
from cosmos.providers.dbt.core.operators.docker import DbtRunOperationDockerOperator, DbtSeedDockerOperator


DBT_ROOT_PATH = os.getenv("DBT_ROOT_PATH", "dags/dbt")
DBT_EXECUTABLE_PATH = os.getenv("DBT_EXECUTABLE_PATH", "/usr/local/airflow/dbt_venv/bin/dbt")

DBT_IMAGE = "dbt_dags:latest"

with DAG(
    dag_id="extract_dag",
    start_date=datetime(2022, 11, 27),
    schedule="@daily",
    doc_md=__doc__,
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "01-EXTRACT"},
) as dag:

    project_seeds = [
        {"project": "jaffle_shop", "seeds": [
            "raw_customers", "raw_payments", "raw_orders"]},
        {"project": "attribution-playbook",
            "seeds": ["customer_conversions", "ad_spend", "sessions"]},
        {"project": "mrr-playbook", "seeds": ["subscription_periods"]},
    ]

    with TaskGroup(group_id="drop_seeds_if_exist") as drop_seeds:
        for project in project_seeds:
            project_dir = os.path.join(DBT_ROOT_PATH, project['project'])
            for seed in project["seeds"]:
                DbtRunOperationDockerOperator(
                    task_id=f"drop_{seed}_if_exists",
                    macro_name="drop_table",
                    args={"table_name": seed},
                    project_dir=project_dir,
                    schema="public",
                    dbt_executable_path=DBT_EXECUTABLE_PATH,
                    conn_id="airflow_db",
                    image=DBT_IMAGE,
                    network_mode="bridge",
                )

    with TaskGroup(group_id="all_seeds") as create_seeds:
        for project in ["jaffle_shop", "mrr-playbook", "attribution-playbook"]:
            project_dir = os.path.join(DBT_ROOT_PATH, project)
            name_underscores = project.replace("-", "_")
            DbtSeedDockerOperator(
                task_id=f"{name_underscores}_seed",
                project_dir=project_dir,
                schema="public",
                dbt_executable_path=DBT_EXECUTABLE_PATH,
                conn_id="airflow_db",
                outlets=[Dataset(f"SEED://{name_underscores.upper()}")],
                image=DBT_IMAGE,
                network_mode="bridge",
            )

    drop_seeds >> create_seeds
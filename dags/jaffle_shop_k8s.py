"""
## Jaffle Shop DAG
[Jaffle Shop](https://github.com/dbt-labs/jaffle_shop) is a fictional eCommerce store. This dbt project originates from
dbt labs as an example project with dummy data to demonstrate a working dbt core project. This DAG uses the cosmos dbt
parser to generate an Airflow TaskGroup from the dbt project folder

"""
import os

from airflow import DAG
from airflow.datasets import Dataset
from airflow.kubernetes.secret import Secret
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from pendulum import datetime


from cosmos.providers.dbt.core.operators.kubernetes import DbtSeedKubernetesOperator, DbtRunKubernetesOperator
from cosmos.providers.dbt.task_group import DbtTaskGroup

PROJECT_DIR = "."

project_seeds = [
        {"project": "jaffle_shop", "seeds": [
            "raw_customers", "raw_payments", "raw_orders"]}
]

postgres_password_secret = Secret(
    deploy_type="env",
    deploy_target="POSTGRES_PASSWORD",
    secret="postgres-secrets",
    key="password",
)

postgres_host_secret = Secret(
    deploy_type="env",
    deploy_target="POSTGRES_HOST",
    secret="postgres-secrets",
    key="host",
)

with DAG(
    dag_id="jaffle_shop_k8s",
    start_date=datetime(2022, 11, 27),
    doc_md=__doc__,
    catchup=False,
) as dag:

    load_seeds = DbtSeedKubernetesOperator( 
        task_id=f"load_seeds", 
        project_dir=PROJECT_DIR, 
        get_logs=True, 
        schema="public", 
        conn_id="postgres_default", 
        image="dbt-jaffle-shop:0.0.7", 
        is_delete_operator_pod=False,
        secrets=[postgres_password_secret, postgres_host_secret] 
    )

    run_models = DbtTaskGroup(
        group_id="jaffle_shop",
        dbt_project_name="jaffle_shop",
        dbt_root_path="./dags/dbt/",
        conn_id="postgres_default",
        execution_mode="kubernetes",
        dbt_args={
            "schema": "public",
            "image": "dbt-jaffle-shop:0.0.7",
            "project_dir": PROJECT_DIR,
            "get_logs": True,
            "conn_id": "postgres_default",
            "image": "dbt-jaffle-shop:0.0.7",
            "is_delete_operator_pod": False,
            "secrets": [postgres_password_secret, postgres_host_secret]
        }
    )

    load_seeds >> run_models

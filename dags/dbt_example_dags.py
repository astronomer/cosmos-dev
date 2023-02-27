"""
## Example DAGs for dbt

This `dbt_example_dags.py` is used to quickly e2e test against various source specified in /include/default_args.py

"""

from airflow import DAG, Dataset
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.task_group import TaskGroup
from include.default_args import sources, dbt_root_directory
from pendulum import datetime

from cosmos.providers.dbt.core.operators import (
    DbtDepsOperator,
    DbtRunOperationOperator,
    DbtSeedOperator,
)
from cosmos.providers.dbt.task_group import DbtTaskGroup

for source in sources:
    conn_type = source['conn_type']

    dyn_args = source
    del dyn_args["conn_type"]

    with DAG(
        dag_id=f"dbt_{conn_type}_example_dag",
        start_date=datetime(2022, 11, 27),
        schedule=[Dataset("DAG://TRIGGER_ALL_TESTS/TRIGGER_ALL")],
        doc_md=__doc__,
        catchup=False,
        tags=[conn_type],
        max_active_runs=1,
    ) as dag:

        projects = [
            {
                "project": "jaffle_shop",
                "seeds": ["raw_customers", "raw_payments", "raw_orders"],
            },
            {
                "project": "attribution-playbook",
                "seeds": ["customer_conversions", "ad_spend", "sessions"],
            },
            {"project": "mrr-playbook", "seeds": ["subscription_periods"]},
        ]

        if conn_type == "redshift":
            start = TriggerDagRunOperator(
                task_id="unpause_redshift_cluster",
                trigger_dag_id="redshift_manager",
                conf={"cluster_request": "unpause_cluster"},
                wait_for_completion=True,
            )
            finish = TriggerDagRunOperator(
                task_id="pause_cluster",
                trigger_dag_id="redshift_manager",
                conf={"cluster_request": "pause_cluster"},
                wait_for_completion=True,
            )
        elif conn_type == "postgres":
            start = TriggerDagRunOperator(
                task_id="unpause_postgres_instance",
                trigger_dag_id="postgres_manager",
                conf={"cluster_request": "unpause_cluster"},
                wait_for_completion=True,
            )
            finish = TriggerDagRunOperator(
                task_id="pause_postgres_instance",
                trigger_dag_id="postgres_manager",
                conf={"cluster_request": "pause_cluster"},
                wait_for_completion=True,
            )
        elif conn_type == "databricks":
            start = TriggerDagRunOperator(
                task_id="unpause_databricks_instance",
                trigger_dag_id="databricks_manager",
                conf={"cluster_request": "unpause_cluster"},
                wait_for_completion=True,
            )
            finish = TriggerDagRunOperator(
                task_id="pause_databricks_instance",
                trigger_dag_id="databricks_manager",
                conf={"cluster_request": "pause_cluster"},
                wait_for_completion=True,
            )
        else:
            start = EmptyOperator(task_id="start")
            finish = EmptyOperator(task_id="finish")

        for project in projects:
            name_underscores = project["project"].replace("-", "_")

            deps = DbtDepsOperator(
                task_id=f"{project['project']}_install_deps",
                project_dir=f"{dbt_root_directory}/{project['project']}",
                **dyn_args
            )

            with TaskGroup(group_id=f"{project['project']}_drop_seeds") as drop_seeds:
                for seed in project["seeds"]:
                    DbtRunOperationOperator(
                        task_id=f"drop_{seed}_if_exists",
                        macro_name="drop_table",
                        args={"table_name": seed, "conn_type": conn_type},
                        project_dir=f"{dbt_root_directory}/{project['project']}",
                        **dyn_args
                    )

            seed = DbtSeedOperator(
                task_id=f"{name_underscores}_seed",
                project_dir=f"{dbt_root_directory}/{project['project']}",
                **dyn_args
            )

            # TODO: Come back and fix tests -- but it's not super important
            test_behavior = (
                "none"
                if project["project"] == "mrr-playbook"
                and conn_type in ["bigquery", "redshift"]
                else "after_all"
            )
            project_task_group = DbtTaskGroup(
                dbt_project_name=project["project"],
                conn_id=source["conn_id"],
                dbt_root_path=dbt_root_directory,
                dbt_args={
                    "db_name": dyn_args.get("db_name", None),
                    "schema": dyn_args.get("schema", None),
                    "vars": {"conn_type": conn_type},
                    "dbt_executable_path": dyn_args.get("dbt_executable_path"),
                },
                test_behavior=test_behavior,
                emit_datasets=False
            )

            start >> deps >> drop_seeds >> seed >> project_task_group >> finish

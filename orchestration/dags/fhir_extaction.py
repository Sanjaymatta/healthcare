from datetime import datetime

from airflow.sdk import DAG, task
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.hooks.base import BaseHook


from pathlib import Path

import yaml


def extract_resource(resource: str):
    print(f"Processing FHIR resource: {resource}")


with DAG(
    dag_id="fhir_extraction",
    description="FHIR resource extraction",
    start_date=datetime(2026, 8, 15),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=10,
    tags=["fhir", "extraction"],
) as dag:

    @task(
            task_id="load_resources"
    )
    def load_resources():
        CONFIG_PATH = (
            Path(__file__).resolve().parents[1]
            / "config"
            / "fhir_resources.yaml"
        )
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        return config["resources"]

    @task(
            task_id="get_checkpoints"
    )
    def get_checkpoints(resources: list[str]):


        INITIAL_START_DATE='2026-08-16 00:00:00'

        hook= SnowflakeHook(
            snowflake_conn_id="snowflake_connection"
        )

        conn = BaseHook.get_connection("snowflake_connection")

        database = conn.extra_dejson["database"]
        schema = conn.extra_dejson["schema"]

        placeholders= ",".join(["%s"]*len(resources))

        sql=f"""
            select  
                 resource_key,
                 last_updated
            from {database}.{schema}.checkpoint
                 where resource_key IN ({placeholders})
        """

        rows =  hook.get_records(
             sql,
             parameters=resources
        )

        checkpoint_map = {
            resource: last_updated
            for resource, last_updated in rows
        }

        results = []

        for resource in resources:
            if resource not in checkpoint_map:
                # New resource
                last_updated = INITIAL_START_DATE

            else:
                last_updated = checkpoint_map[resource]

                if last_updated is None:
                    raise ValueError(
                        f"Checkpoint exists for {resource}, "
                        "but last_updated is NULL"
                    )

            results.append(
                {
                    "resource": resource,
                    "last_updated": str(last_updated),
                }
            )
        return results

    @task(
            task_id="extract_resources"
    )
    def extract_resources(resource: str):
        print(f"Processing FHIR resource: {resource}")

    


    resources = load_resources()
    checkpoints = get_checkpoints(resources)
    # extract_resources.expand(
    #     resource=resources
    # )
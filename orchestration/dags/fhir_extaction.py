from datetime import datetime

from airflow.sdk import DAG, task, get_current_context
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.hooks.base import BaseHook
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator

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
            task_id="generate_run_id"
    )
    def get_run_id():
        context = get_current_context()
        return context["dag_run"].run_id

    @task(
    task_id="build_ecs_inputs"
    )
    def build_ecs_inputs(checkpoints, execution_id):

        return [
            {
                "containerOverrides": [
                    {
                        "name": "fhir-extractor",
                        "command": [
                            "--resource",
                            item["resource"],
                            "--last-updated",
                            str(item["last_updated"]),
                            "--run-id",
                            execution_id,
                            "--s3-prefix",
                            "raw/fhir",
                        ],
                    }
                ]
            }
            for item in checkpoints
        ]

    

    


    resources = load_resources()
    checkpoints = get_checkpoints(resources)
    execution_id = get_run_id()
    ecs_inputs = build_ecs_inputs(
        checkpoints,
        execution_id,
    )   

    ecs_tasks = EcsRunTaskOperator.partial(

        task_id="extract_resource",
        cluster="{{ var.json.FHIR_ECS_CONFIG.cluster }}",
        task_definition="{{ var.json.FHIR_ECS_CONFIG.task_definition }}",
        # cluster="fhir-local-cluster",
        # task_definition="fhir-extractor:8",
        launch_type="FARGATE",
        
        wait_for_completion=True,
        deferrable=True,
        ).expand(
            overrides=ecs_inputs
    )

       
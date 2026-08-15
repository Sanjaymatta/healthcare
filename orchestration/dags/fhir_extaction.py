from datetime import datetime

from airflow.sdk import DAG, task
from airflow.providers.standard.operators.python import PythonOperator

from utils.config_loader import load_fhir_resources

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

    @task
    def load_resources():
        CONFIG_PATH = (
            Path(__file__).resolve().parents[1]
            / "config"
            / "fhir_resources.yaml"
        )
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        return config["resources"]

    @task
    def extract_resources(resource: str):
        print(f"Processing FHIR resource: {resource}")


    resources = load_resources()
    extract_resources.expand(
        resource=resources
    )
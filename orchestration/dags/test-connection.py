from datetime import datetime

from airflow.sdk import DAG, task
from airflow.providers.standard.operators.python import PythonOperator

from utils.config_loader import load_fhir_resources

from pathlib import Path

import yaml
import boto3
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook



with DAG(
    dag_id="test_connection",
    description="FHIR resource extraction testing cinnections",
    start_date=datetime(2026, 8, 15),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=10,
    tags=["fhir", "extraction"],
) as dag:

   

    @task
    def test_secrets():
      client = boto3.client("secretsmanager")
      response = client.get_secret_value(
              SecretId="snowflake_connection"
          )
      print(response["SecretString"])


    @task
    def test_snowflake_connection():

        hook = SnowflakeHook(
            snowflake_conn_id="snowflake_fhir"
        )

        result = hook.get_first("SELECT CURRENT_TIMESTAMP()")

        print(result)    

    # test_secrets()
    test_snowflake_connection()

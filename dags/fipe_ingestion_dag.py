import sys
import os

# Adiciona o caminho da pasta raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_ingestion.insercao_dados import get_fipe

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

dag = DAG(
    'fipe_ingestion_dag',
    default_args=default_args,
    description='DAG para ingestão de dados da API FIPE',
    schedule_interval='@daily',
)

t1 = PythonOperator(
    task_id='get_fipe_data',
    python_callable=get_fipe,
    dag=dag,
)

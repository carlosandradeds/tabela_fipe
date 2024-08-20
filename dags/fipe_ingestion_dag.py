import sys
import os

# Adiciona o caminho da pasta raiz ao sys.path
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

from data_ingestion.insercao_dados import get_fipe, Session

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

def run_fipe():
    session = Session()
    try:
        get_fipe(session)
    finally:
        session.close()

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'fipe_ingestion_dag',
    default_args=default_args,
    description='DAG para ingestão de dados da API FIPE',
    start_date=datetime(2024, 8, 20),
    schedule_interval='@daily',
)

t1 = PythonOperator(
    task_id='get_fipe_data',
    python_callable=get_fipe,
    dag=dag,
)

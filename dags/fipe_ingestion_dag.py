from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from data_ingestion.insercao_dados import get_fipe

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(minutes=1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fipe_ingestion_dag',
    default_args=default_args,
    description='DAG para ingestão de dados da Tabela Fipe',
    schedule_interval=timedelta(days=3),
)

def ingest_data():
    get_fipe()

ingest_task = PythonOperator(
    task_id='ingest_data_task',
    python_callable=ingest_data,
    dag=dag,
)

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
import datetime
import os

from sqlalchemy import create_engine

default_args = {
    'owner': 'niko_huy',
    'start_date': datetime.datetime(2020, 2, 18),
    'provide_context': True,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    'execution_timeout': datetime.timedelta(minutes=60),
    'pool': 'default_pool',
    'templates_dict': {
        'airflow_db': os.environ.get('AIRFLOW__CORE__SQL_ALCHEMY_CONN'),
    }
}


def cleanup_airflow_db(templates_dict, **context):
    engine = create_engine(templates_dict['airflow_db'])
    with engine.connect() as conn:
        for statement in [
            "delete from log where true;",
            "delete from task_instance where true;",
            "delete from job where true;",
            "delete from dag_run where true;"
            "delete from task_fail where true;"
        ]:
            conn.execute(statement)


dag = DAG('cleanup_airflow_DAG',
          schedule_interval='0 0 * * *',
          description=f'''Scrape website for newspaper''',
          default_args=default_args,
          catchup=False,
          )

with dag:
    cleanup = PythonOperator(task_id=f'cleanup_airflow_db', python_callable=cleanup_airflow_db)

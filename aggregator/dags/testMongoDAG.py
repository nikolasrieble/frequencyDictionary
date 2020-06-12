from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from mongo_plugin.hooks.mongo_hook import MongoHook

from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

def helloMongo():
    myclient = MongoHook(conn_id='NEWSPAPER_DB')
    #mydb = myclient['statistics']
    #mycol = mydb['summary']
    mycol.insert_one('Summary',{"test": datetime.now()})

 
testMongoDAG = DAG(
    "testMongoDAG",
    default_args=default_args,
    schedule_interval="0 0 1 * * ",
    catchup=False,
    max_active_runs=1,
)

doit = PythonOperator(
    task_id='time_cohorts',
    python_callable=helloMongo,
    dag=testMongoDAG,
)

from newspaper import Article
import pymongo
from airflow.models import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.python_operator import PythonOperator
import datetime
import os

from newspaper import ArticleException

default_args = {
    'owner': 'niko_huy',
    'start_date': datetime.datetime(2020, 2, 18),
    'provide_context': True,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    'execution_timeout': datetime.timedelta(minutes=60),
    'pool': 'default_pool'
}


def url_processor(**context):

    myclient = get_db_client()

    timestamp = datetime.datetime.now()
    target_dict = get_article_to_scrape(myclient)

    if target_dict is not None:
        article = Article(target_dict["url"])

        try:
            article.download()
            article.parse()

            data = extract_data(article)
            data["fetched_at"] = timestamp

            collection = get_collection(myclient, target_dict["language"])
            # prevent duplicates
            if collection.count_documents({'headline': article.title}) == 0:
                collection.insert_one(data)

            update_todo_list(myclient, target_dict)

        except ArticleException:
            print('article could not be scraped from url {}'.format(article.url))


def update_todo_list(myclient, target_dict):
    mydb = myclient['TODO']
    db = mydb['TODO']
    return db.update_one({'url': target_dict['url']}, {'$set': {'scraped': 1}}, upsert=False)


def get_db_client():
    mongodb_string = os.environ.get('MONGO_DB')
    assert mongodb_string
    myclient = pymongo.MongoClient(mongodb_string)
    return myclient


def get_article_to_scrape(myclient):
    mydb = myclient['TODO']
    db = mydb['TODO']
    return db.find_one({'scraped': 0})


def get_collection(myclient, language):
    mydb = myclient['newspaper']
    collection = mydb[language]
    return collection


def extract_data(article):
    return {
        'published_at': article.publish_date,
        'text': article.text,
        'authors': list(article.authors),
        'headline': article.title,
        'url': article.url,
        'tags': list(article.tags)
    }


def conditionally_trigger(context, dag_run_obj):
    myclient = get_db_client()
    if get_article_to_scrape(myclient) is not None:
        return dag_run_obj


dag = DAG('url_processor_dag',
          schedule_interval='* * * * *',
          description='Scrape website for newspaper',
          default_args=default_args,
          catchup=False,
          )

with dag:
    processor = PythonOperator(task_id='url_processor_operator',
                               python_callable=url_processor)
    trigger = TriggerDagRunOperator(
        task_id='trigger_url_processor_operator',
        trigger_dag_id="url_processor_dag",
        python_callable=conditionally_trigger
    )
    trigger.set_upstream(processor)

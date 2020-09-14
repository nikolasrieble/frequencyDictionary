import newspaper
import pymongo
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
import datetime
import os
import psutil

from newspaper import ArticleException

default_args = {
    'owner': 'niko_huy',
    'start_date': datetime.datetime(2020, 2, 18),
    'provide_context': True,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    'execution_timeout': datetime.timedelta(minutes=60),
    'pool': 'default_pool',
    'templates_dict': {
        'mongodb_string': os.environ.get('MONGO_DB'),
    }
}

input_list = {
    'tr': 'https://www.sozcu.com.tr/',
    'de': 'https://www.faz.net/',
}


def url_scraper(templates_dict, language, **context):
    collection = get_collection(templates_dict)
    newspaper_url = input_list.get(language)

    paper = newspaper.build(newspaper_url,
                            language=language,
                            memoize_articles=False,
                            fetch_images=False,
                            MIN_WORD_COUNT=100)

    for article in paper.articles:
        # prevent duplicates
        if collection.count_documents({'url': article.url}) == 0:
            collection.insert_one({'url': article.url,
                                   'scraped': 0,
                                   'language':language})


def get_collection(templates_dict):
    mongodb_string = templates_dict.get('mongodb_string')
    assert mongodb_string
    myclient = pymongo.MongoClient(mongodb_string)
    mydb = myclient['TODO']
    collection = mydb['TODO']
    return collection


dag = DAG('url_scraper',
          schedule_interval='0 */12 * * *',
          description=f'''Scrape website for newspaper''',
          default_args=default_args,
          catchup=False,
          )

with dag:
    tr_scraper = PythonOperator(task_id=f'url_scraper_tr', python_callable=url_scraper,
                                op_kwargs={'language': 'tr'})
    de_scraper = PythonOperator(task_id=f'url_scraper_de', python_callable=url_scraper,
                                op_kwargs={'language': 'de'})
    de_scraper.set_upstream(tr_scraper)

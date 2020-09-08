import newspaper
import pymongo
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
import datetime
import os

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


def newspaper_scraper(templates_dict, language, **context):
    collection = get_collection(language, templates_dict)
    newspaper_url = input_list.get(language)
    timestamp = datetime.datetime.now()

    paper = newspaper.build(newspaper_url, language=language, memoize_articles=False, MIN_WORD_COUNT=100)
    for article in paper.articles:
        article.download()
        article.parse()

        data = extract_data(article)
        data["fetched_at"] = timestamp

        # prevent duplicates
        if collection.count_documents({'headline': article.title}) == 0:
            collection.insert_one(data)

    return


def get_collection(language, templates_dict):
    mongodb_string = templates_dict.get('mongodb_string')
    assert mongodb_string
    myclient = pymongo.MongoClient(mongodb_string)
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


dag = DAG('newspaper_scraper',
          schedule_interval='0 0 * * 0',
          description=f'''Scrape website for newspaper''',
          default_args=default_args,
          catchup=False,
          )

with dag:
    tr_scraper = PythonOperator(task_id=f'newspaper_scraper_tr', python_callable=newspaper_scraper,
                                op_kwargs={'language': 'tr'})
    de_scraper = PythonOperator(task_id=f'newspaper_scraper_de', python_callable=newspaper_scraper,
                                op_kwargs={'language': 'de'})
    de_scraper.set_upstream(tr_scraper)

if __name__ == '__main__':
    from pathlib import Path
    import sys

    cwd = Path.cwd()
    root = cwd.parent.parent
    sys.path.append(str(root))

    try:
        from passwords import password

        mongodb = password['mongodb']
        user = mongodb['user']
        pw = mongodb['password']
        url = mongodb['url']
        conn_str = f'mongodb+srv://{user}:{pw}@{url}'
    except:
        conn_str = os.environ.get('MONGO_DB')

    templates_dict = {'mongodb_string': conn_str}
    newspaper_scraper(templates_dict, language='de')

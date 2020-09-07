import datetime
import newspaper
import os
import pymongo
from bs4 import BeautifulSoup
from dateutil.parser import parse
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

input_list = {
    'tr': 'https://www.sozcu.com.tr/',
    'de': 'https://www.faz.net/',
}


def newspaper_scraper(templates_dict, language, **context):
    mongodb_string = templates_dict.get('mongodb_string')
    assert mongodb_string
    myclient = pymongo.MongoClient(mongodb_string)
    mydb = myclient['newspaper']

    collection = mydb[language]
    newspaper_url = input_list.get(language)

    paper = newspaper.build(newspaper_url, language=language, memoize_articles=False, MIN_WORD_COUNT=500)
    for article in paper.articles:
        article.download()
        article.parse()

        url = article.url
        authors = list(article.authors)
        date_time = article.publish_date
        title = article.title
        text = article.text
        tags = list(article.tags)

        if not article.publish_date:
            soup = BeautifulSoup(article.html, 'html.parser')
            try:
                date_time = soup.find('time')['datetime']
                date_time = parse(date_time).strftime('%Y-%m-%d')
            except:
                date_time = datetime.datetime.now()

        # prevent duplicates
        if collection.count_documents({'headline': article.title}) == 0:
            collection.insert_one({
                'text': text,
                'authors': authors,
                'fetched_at': date_time,
                'headline': title,
                'url': url,
                'tags': tags
            })

    return


dag_id = 'newspaper_scraper'
schedule = '0 0 * * 0'
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

dag = DAG(dag_id,
          schedule_interval=schedule,
          description=f'''Scrape website for newspaper''',
          default_args=default_args,
          catchup=False,
          )

with dag:
    for language in input_list.keys():
        scraper = PythonOperator(task_id=f'newspaper_scraper_{language}', python_callable=newspaper_scraper,
                                 op_kwargs={'language': language})

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

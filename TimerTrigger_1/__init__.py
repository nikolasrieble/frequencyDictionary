import datetime
import logging
import pymongo
import azure.functions as func
import newspaper
import os


input_list = [
    ('tr', 'https://www.sozcu.com.tr/'),
    ('de', 'https://www.faz.net/')
    ]


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')

    conn = os.environ.get('MONGO_DB')
    myclient = pymongo.MongoClient(conn)
    mydb = myclient['newspaper']

    for language, url in input_list:
        collection = mydb[language]

        paper = newspaper.build(url, language=language, memoize_articles=False)
        for article in paper.articles:
            article.download()
            article.parse()
            collection.insert_one({
            'text' : article.text,
            'fetched_at' : datetime.datetime.now(),
            'headline' : article.title,
            'url': article.url})
            
    logging.info('Python timer trigger function ran at %s', utc_timestamp)

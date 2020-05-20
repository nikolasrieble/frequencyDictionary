import datetime
import logging
import pymongo
import azure.functions as func
import newspaper
from utils.get_connection import get_connection

# todo: take out this configuration somewhere else
input_list = [
    ('tr', 'https://www.sozcu.com.tr/'),
    ('de', 'https://www.faz.net/')
]


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')

    myclient = pymongo.MongoClient(get_connection())
    mydb = myclient['newspaper']

    for language, url in input_list:
        collection = mydb[language]

        paper = newspaper.build(url, language=language, memoize_articles=False)
        for article in paper.articles:
            article.download()
            article.parse()

            # prevent duplicates
            if collection.count_documents({'headline': article.title}) == 0:
                collection.insert_one({
                    'text': article.text,
                    'fetched_at': datetime.datetime.now(),
                    'headline': article.title,
                    'url': article.url})

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

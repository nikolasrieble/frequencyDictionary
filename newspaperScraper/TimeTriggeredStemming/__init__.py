import datetime
import logging

import azure.functions as func
from utils.get_connection import get_mydb


def extract_words(article):
    # TODO : Implement nlp logic here
    return None


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    mydb = get_mydb()

    for name in mydb.collection_names():
        logging.info('now checking collection %s', name)
        collection = mydb[name]

        # get all collection for which a statistic has not been computed
        cursor = collection.find({"unique_words": None})
        for article in cursor:
            unique_words = None  # extract_words(article["text"])

            collection.update_one(
                {"url": article["url"]},  # update the document identified by the given url
                {"unique_words": unique_words})  # with the list of unique words

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

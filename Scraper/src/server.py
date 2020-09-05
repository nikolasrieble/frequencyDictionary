import datetime
import json
import os

import dacite
import newspaper
from flask import Flask
from flask_apscheduler import APScheduler
from newspaper import ArticleException

from configuration import Configuration
from database import Database

with open('configuration.json', 'r') as json_file:
    raw_config = json_file.read()
Config = dacite.from_dict(data_class=Configuration, data=json.loads(raw_config))

app = Flask(__name__)
scheduler = APScheduler()
database = Database(Config.database)


@app.route('/')
def welcome():
    return 'Welcome to flask_apscheduler demo', 200


@app.route('/trigger_scraper')
def trigger_scrape():
    scrape()
    return 'Scraping triggered', 200


@scheduler.task('interval', id='health', minutes=10, misfire_grace_time=900)
def health():
    print("I am healthy")


@scheduler.task('interval', id='scrape', hours=12, misfire_grace_time=900)
def scrape():
    for language, url in [
        ('de', 'https://www.faz.net/')
    ]:
        paper = newspaper.build(url, language=language, memoize_articles=False)
        for article in paper.articles:

            try:
                article.download()
                article.parse()

                database.insert(
                    {
                        'text': article.text,
                        'fetched_at': datetime.datetime.now(),
                        'title': article.title,
                        'url': article.url
                    }
                )
            except ArticleException:
                continue
    print('Ran scrape function')


if __name__ == '__main__':
    app.config.from_object(Config.backend)

    # it is also possible to enable the API directly
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

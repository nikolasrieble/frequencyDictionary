import datetime
import json

import dacite
import newspaper
from flask import Flask
from flask_apscheduler import APScheduler

from Scraper.src.configuration import Configuration
from Scraper.src.database import Database

with open('../configuration.json', 'r') as json_file:
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
            article.download()
            article.parse()

            database.insert(
                {
                    'text': article.text,
                    'fetched_at': datetime.datetime.now(),
                    'headline': article.title,
                    'url': article.url
                }
            )

    print('Ran scrape function')


if __name__ == '__main__':
    app.config.from_object(Config.backend)

    # it is also possible to enable the API directly
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0', port=12345)

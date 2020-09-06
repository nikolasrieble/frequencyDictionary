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

with open('../configuration.json', 'r') as json_file:
    raw_config = json_file.read()
Config = dacite.from_dict(data_class=Configuration, data=json.loads(raw_config))

app = Flask(__name__)
app.target = None
scheduler = APScheduler()
database = Database(Config.database)

DEFAULT_TARGET = '[{"language":"de", "url":"https://www.faz.net/"}]'
DEFAULT_PORT = 5000


@app.route('/')
def welcome():
    return 'Welcome to flask_apscheduler demo', 200


@app.route('/test_scraper')
def test_scraper():
    scrape(limit=1)
    return 'Scraping test triggered', 200


@app.route('/trigger_scraper')
def trigger_scraper():
    scrape()
    return 'Scraping triggered', 200


@app.route('/reload_target')
def reload_target():
    load_target()
    return 'Target set to {}'.format(app.target), 200


@scheduler.task('interval', id='health', minutes=10, misfire_grace_time=900)
def health():
    print("I am healthy")


@scheduler.task('interval', id='scrape', hours=12, misfire_grace_time=900)
def scrape(limit: int = None):
    for target in app.target:
        paper = newspaper.build(target['url'], language=target['language'], memoize_articles=False)
        for idx, article in enumerate(paper.articles):

            if limit:
                if idx > limit:
                    break

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


def load_target():
    target_configuration = os.environ.get('TARGET', DEFAULT_TARGET)
    app.target = json.loads(target_configuration)


if __name__ == '__main__':
    app.config.from_object(Config.backend)
    load_target()
    # it is also possible to enable the API directly
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()

    port = int(os.environ.get('PORT', DEFAULT_PORT))
    app.run(debug=True)

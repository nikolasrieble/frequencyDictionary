import pymongo

from Scraper.src.configuration import MongoConfiguration


class Database:

    def __init__(self, configuration: MongoConfiguration):
        pass

    def insert(self, data: dict):
        print(data)


class MongoDB:

    def __init__(self, configuration: MongoConfiguration):
        self.collection = None
        self.configuration = configuration

    def connect(self):
        connection_string = f'mongodb+srv://{self.configuration.user}:{self.configuration.pw}@{self.configuration.url}'
        mongo_client = pymongo.MongoClient(connection_string)
        database = mongo_client[self.configuration.database]
        self.collection = database[self.configuration.collection]

    def insert(self, data: dict):
        if self.collection.count_documents({'title': data["title"]}) == 0:
            self.collection.insert_one(data)

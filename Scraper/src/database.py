import pymongo

from configuration import MongoConfiguration


class Database:

    def __init__(self, configuration: MongoConfiguration = None):
        if configuration is not None:
            self.db = MongoDB(configuration)
        pass

    def insert(self, data: dict):
        if self.db is not None:
            self.db.insert(data)
        else:
            print(data)


class MongoDB:

    def __init__(self, configuration: MongoConfiguration):
        self.collection = None
        self.configuration = configuration

    def connect(self):
        connection_string = f'mongodb+srv://{self.configuration.user}:{self.configuration.pw}@{self.configuration.url}/{self.configuration.database}?retryWrites=true&w=majority'
        mongo_client = pymongo.MongoClient(connection_string)
        database = mongo_client[self.configuration.database]
        self.collection = database[self.configuration.collection]

    def insert(self, data: dict):
        try:
            self._insert(data)
        except:
            self.connect()
            self._insert(data)

    def _insert(self, data):
        if self.collection.count_documents({'title': data["title"]}) == 0:
            self.collection.insert_one(data)

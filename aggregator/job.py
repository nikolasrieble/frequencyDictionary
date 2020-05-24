from datetime import datetime
import pymongo

def helloMongo():
    MONGO_DB = "mongodb+srv://newspaperScraper:eQUoQcPeMZdA2jze@cluster1-qrhh1.azure.mongodb.net/test?retryWrites=true&w=majority"
    myclient = pymongo.MongoClient(MONGO_DB)
    mydb = myclient['statistics']
    mycol = mydb['summary']
    mycol.insert_one({"test": datetime.now()})

helloMongo()

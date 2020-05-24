import pymongo


def get_connection():
    try:
        from utils.conn_str import conn_str
        return conn_str
    except:
        import os
        return os.environ.get('MONGO_DB')


def get_mydb():
    myclient = pymongo.MongoClient(get_connection())
    mydb = myclient['newspaper']

    return mydb

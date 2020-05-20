def get_connection():
    try:
        from utils.conn_str import conn_str
        return conn_str
    except:
        import os
        return os.environ.get('MONGO_DB')


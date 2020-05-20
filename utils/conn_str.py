from secrets import password

mongodb = password['mongodb']
user = mongodb['user']
pw = mongodb['password']
url = mongodb['url']
conn_str = f'mongodb+srv://{user}:{pw}@{url}'

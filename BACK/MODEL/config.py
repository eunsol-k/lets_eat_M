db = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': 3307,
    'database': 'yack_test'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
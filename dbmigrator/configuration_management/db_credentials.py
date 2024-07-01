import os
from dotenv import load_dotenv

#path = 'databases'

class DBCredentials:
    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port


def mysql_credentials():
    load_dotenv() #dotenv_path=path
    return DBCredentials(
        database=os.environ.get("MYSQL_DATABASE"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        host=os.environ.get("MYSQL_HOST"),
        port=os.environ.get("MYSQL_PORT")
    )

def postgres_credentials():
    load_dotenv() #dotenv_path=path
    return DBCredentials(
        database=os.environ.get("POSTGRES_DBNAME"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT")
    )
   


import mysql.connector # DB에 연결하기 위한 라이브러리

from config import Config

def get_connection(): 

    connection = mysql.connector.connect(
        host = Config.HOST ,
        database = Config.DATABASE,
        user = Config.DB_USER,
        password = Config.DB_PASSWORD
    )
    return connection


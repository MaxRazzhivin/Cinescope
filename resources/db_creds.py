import os
from dotenv import load_dotenv

load_dotenv()

class MoviesDbCreds:
    HOST = os.getenv('DB_MOVIES_HOST')
    PORT = os.getenv('DB_MOVIES_PORT')
    DATABASE_NAME = os.getenv('DB_MOVIES_NAME')
    USERNAME = os.getenv('DB_MOVIES_USERNAME')
    PASSWORD = os.getenv('DB_MOVIES_PASSWORD')

    @classmethod
    def as_dict(cls):
        return dict(
            host=cls.HOST,
            port=cls.PORT,
            dbname=cls.DATABASE_NAME,
            user=cls.USERNAME,
            password=cls.PASSWORD,
        )

    # теперь можем через psycopg2.connect(**MoviesDbCreds.as_dict()) соединяться с БД
from os import getenv
from dotenv import load_dotenv
from wallet.db.storage import DatabaseManager

load_dotenv()


def get_database():
    if getenv("TESTING") == "True":
        db_url = getenv("DB_FOR_TEST_URL")
    else:
        db_url = getenv("DATABASE_URL")
    database = DatabaseManager(db_url)
    return database, db_url

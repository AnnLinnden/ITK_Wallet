from os import getenv
from dotenv import load_dotenv
from wallet.db.storage import DatabaseManager

load_dotenv()
database_url = getenv('DATABASE_URL')
database = DatabaseManager(database_url)



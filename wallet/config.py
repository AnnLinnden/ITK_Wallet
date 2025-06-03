from os import getenv
from dotenv import load_dotenv
from wallet.db.storage import DatabaseManager

load_dotenv()

is_testing = getenv("TESTING", "False") == "True"

db_url = (
    getenv("DB_FOR_TEST_URL")
    if is_testing
    else getenv("DATABASE_URL")
)

database = DatabaseManager(db_url)



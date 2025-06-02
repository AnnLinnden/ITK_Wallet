import logging
from os import getenv
from dotenv import load_dotenv
from wallet.db.storage import DatabaseManager

load_dotenv()
database_url = getenv('DATABASE_URL')
database = DatabaseManager(database_url)

handler_console = logging.StreamHandler()
handler_file = logging.FileHandler('app.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[handler_file, handler_console])
logger = logging.getLogger(__name__)



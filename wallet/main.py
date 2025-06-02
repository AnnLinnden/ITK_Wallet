import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from wallet.config import database

handler_console = logging.StreamHandler()
handler_file = logging.FileHandler('app.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[handler_file, handler_console])
logger = logging.getLogger(__name__)


@asynccontextmanager  # .on_event("startup") устарел
async def lifespan(app: FastAPI):
    logger.info('Запуск приложения')
    try:
        await database.create_tables()
        logger.info('Таблицы готовы к работе')
    except Exception as e:
        logger.error(f'Ошибка при создании таблиц: {e}')
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/api/v1/wallets/{WALLET_UUID}")
async def get_wallet_info(wallet_uuid: str) -> dict:
    wallet_balance = await database.get_wallet_balance(wallet_uuid)
    return {"uuid": wallet_uuid, "balance": wallet_balance}


@app.post("api/v1/wallets/{WALLET_UUID}/deposit")
async def deposit_to_wallet(wallet_uuid: str, amount: int):
    database.increase_wallet_balance(wallet_uuid, amount)
    return f'Баланс кошелька {wallet_uuid} увеличен на {amount}'


@app.post("api/v1/wallets/{WALLET_UUID}/withdraw")
async def withdraw_from_wallet(wallet_uuid: str, amount: int):
    database.decrease_wallet_balance(wallet_uuid, amount)
    return f'Баланс кошелька {wallet_uuid} уменьшен на {amount}'

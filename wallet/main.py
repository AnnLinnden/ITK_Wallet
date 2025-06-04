import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from wallet.config import get_database
from wallet.db.models.schemas import Amount

handler_console = logging.StreamHandler()
handler_file = logging.FileHandler('app.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[handler_file, handler_console])
logger = logging.getLogger(__name__)

database = get_database()[0]


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


@app.get("/api/v1/wallets/{wallet_uuid}")
async def get_wallet_info(wallet_uuid: str) -> dict:
    try:
        wallet_balance = await database.get_wallet_balance(wallet_uuid)
        return {"uuid": wallet_uuid, "balance": wallet_balance}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Не удалось получить информацию о кошельке: {e}')


@app.post("/api/v1/wallets/{wallet_uuid}/deposit")
async def deposit_to_wallet(wallet_uuid: str, amount: Amount):
    try:
        await database.increase_wallet_balance(wallet_uuid, amount.amount)
        return f'Баланс кошелька {wallet_uuid} увеличен на {amount.amount}'  # amount.amount для корректного ответа
        # из модели pydantic
    except Exception as e:
        logger.error(f'Ошибка при увеличении баланса: {e}')
        raise HTTPException(status_code=500, detail=f'Ошибка при увеличении баланса: {e}')  # 500 - потому что,
        # скорее всего, проблема на нашей стороне, а не у пользователя


@app.post("/api/v1/wallets/{wallet_uuid}/withdraw")
async def withdraw_from_wallet(wallet_uuid: str, amount: Amount):
    try:
        await database.decrease_wallet_balance(wallet_uuid, amount.amount)
        return f'Баланс кошелька {wallet_uuid} уменьшен на {amount.amount}'
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Ошибка при уменьшении баланса: {e}')  # а тут скорее проблема
        # с запросом, то есть на стороне пользователя


if __name__ == "__main__":  # не использовать в продакшене!
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from wallet.config import database

app = FastAPI()


@app.get("/api/v1/wallets/{WALLET_UUID}")
async def get_wallet_info(wallet_uuid: str) -> dict:
    wallet_balance = await database.get_wallet_balance(wallet_uuid)
    return {"uuid": wallet_uuid, "balance": wallet_balance}


@app.post("api/v1/wallets/{WALLET_UUID}/deposit")
async def deposit_to_wallet(wallet_uuid: str, amount: int):
    pass


@app.post("api/v1/wallets/{WALLET_UUID}/withdraw")
async def withdraw_from_wallet(wallet_uuid: str, amount: int):
    pass

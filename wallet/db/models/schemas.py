from pydantic import BaseModel


class Wallet(BaseModel):
    uuid: str
    balance: int

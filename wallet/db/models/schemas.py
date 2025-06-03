from pydantic import BaseModel, Field


class Wallet(BaseModel):
    uuid: str
    balance: int


class Amount(BaseModel):  # проверяем, что пользователь при изменении баланса вводит положительное число
    amount: int = Field(gt=0)

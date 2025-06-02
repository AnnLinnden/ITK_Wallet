from sqlmodel import SQLModel, Field


class Wallet(SQLModel, table=True):
    uuid: str = Field(primary_key=True)
    balance: int = Field(default=0)

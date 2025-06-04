from sqlalchemy import text, select
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models.sql_models import Wallet


class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_async_engine(database_url)
        self.async_session = async_sessionmaker(self.engine,
                                                class_=AsyncSession,
                                                expire_on_commit=False)
        self.wallet = Wallet

    async def create_wallet(self, wallet_uuid: str, balance: int) -> None:
        async with self.async_session() as session:
            new_wallet = self.wallet(uuid=wallet_uuid, balance=balance)
            session.add(new_wallet)
            await session.commit()

    async def get_wallet_balance(self, wallet_uuid: str) -> int:
        async with self.async_session() as session:
            wallet_obj = await session.get(self.wallet, wallet_uuid)
            if wallet_obj is None:
                raise Exception(f'Кошелек {wallet_uuid} не найден')
            else:
                return wallet_obj.balance

    async def increase_wallet_balance(self, wallet_uuid: str, amount: int) -> None:
        async with self.async_session() as session:
            wallet_obj = await session.execute(
                select(self.wallet)
                .where(self.wallet.uuid == wallet_uuid)
                .with_for_update())
            result = wallet_obj.scalars().one_or_none()
            if not result:
                await self.create_wallet(wallet_uuid, amount)
            else:
                result.balance += amount
                await session.commit()

    async def decrease_wallet_balance(self, wallet_uuid: str, amount: int) -> None:
        async with self.async_session() as session:
            wallet_obj = await session.execute(
                select(self.wallet)
                .where(self.wallet.uuid == wallet_uuid)
                .with_for_update())
            result = wallet_obj.scalars().one_or_none()
            if not result:
                await self.create_wallet(wallet_uuid, 0)  # создаем кошелек в любом случае
                raise Exception(f'Кошелек {wallet_uuid} имеет нулевой баланс. Не хватает средств для вывода')
            if result.balance >= amount:
                result.balance -= amount
                await session.commit()
            else:
                raise Exception(f'Недостаточно средств на кошельке {wallet_uuid}')

    async def check_tables_exist(self) -> bool:
        async with self.engine.connect() as conn:
            result_for_wallet_table = await conn.execute(
                text("SELECT to_regclass('public.wallet')"))  # используем стандартную схему PostgreSQL - public
            table_wallet_exists = result_for_wallet_table.scalar()
            return table_wallet_exists

    async def create_tables(self):
        tables_exist = await self.check_tables_exist()
        if not tables_exist:
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)




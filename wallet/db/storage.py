from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_async_engine(database_url)
        async_session = async_sessionmaker(self.engine,
                                           class_=AsyncSession,
                                           expire_on_commit=False)

    async def get_wallet_balance(self, wallet_uuid: str) -> int:
        pass

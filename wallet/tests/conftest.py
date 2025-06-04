import asyncio
import pytest_asyncio
from sqlmodel import SQLModel
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import uuid
from wallet.config import get_database
from wallet.db.models.sql_models import Wallet
from wallet.main import app

database, db_url = get_database()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest_asyncio.fixture(autouse=True)
async def prepare_test_db():
    test_engine = create_async_engine(db_url, echo=True)
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        print("Таблицы удалены")
        await conn.run_sync(SQLModel.metadata.create_all)
        print("Таблицы созданы")
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    # Создает движок с подключением к тестовой базе данных
    engine = create_async_engine(db_url, echo=True) # Параметр echo=True включает вывод SQL-запросов в консоль для отладки.
    yield engine # Выдает движок для использования в тестах.
    await engine.dispose() # и освобождает ресурсы движка (engine.dispose()).

@pytest_asyncio.fixture
async def test_db_session(db_engine) -> AsyncSession:
    async with AsyncSession(db_engine) as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_db_session):
    database.async_session = lambda: test_db_session
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(autouse=True)
async def cleanup(request, test_db_session):
    yield
    await test_db_session.rollback()


@pytest_asyncio.fixture
async def fill_test_table(test_db_session):
    first_wallet = Wallet(uuid=str(uuid.uuid4()), balance=0)
    second_wallet = Wallet(uuid=str(uuid.uuid4()), balance=100)
    third_wallet = Wallet(uuid=str(uuid.uuid4()), balance=500)
    test_db_session.add_all([first_wallet, second_wallet, third_wallet])
    await test_db_session.commit()

    # Вместо ленивой загрузки загружаем актуальное состояние немедленно. Без этого словим greenlet_spawn
    for wallet in [first_wallet, second_wallet, third_wallet]:
        await test_db_session.refresh(wallet)
        _ = wallet.uuid
        _ = wallet.balance

    return {"zero balance": first_wallet, "100 balance": second_wallet, "500 balance": third_wallet}

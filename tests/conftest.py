import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base
from app.config import settings

@pytest_asyncio.fixture(scope="function")
async def client():
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)


    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("DELETE FROM transactions"))
        await conn.execute(text("DELETE FROM wallets"))

    
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM transactions"))
        await conn.execute(text("DELETE FROM wallets"))
    await engine.dispose()
    app.dependency_overrides.pop(get_db, None)
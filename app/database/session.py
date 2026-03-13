from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker

from .model import Base
from ..settings import db_settings

aengine: AsyncEngine = create_async_engine(
    url=db_settings.get_url(),
    echo=True
)

asession = async_sessionmaker(aengine)

async def create_tables():
    async with aengine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with asession() as session:
        yield session

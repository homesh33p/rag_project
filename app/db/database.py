from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from langchain_postgres import PGEngine

from app.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("postgresql+psycopg2"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg")

engine = create_async_engine(DATABASE_URL, echo=False)
pg_engine = PGEngine.from_engine(engine=engine)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def init_db():
    from app.embeddings.initialise_emb_tbl import EmbeddingsTable
    await EmbeddingsTable.create()

async def get_db():
    db = async_session_maker()
    try:
        yield db
    finally:
        await db.close()

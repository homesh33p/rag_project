from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
pguser = os.getenv("RAG_USER")
pgpass = os.getenv("RAG_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql+psycopg2://{pguser}:{pgpass}@localhost:5432/rag")
# Convert to async URL if needed
if DATABASE_URL.startswith("postgresql+psycopg2"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        # Import models to ensure they are registered
        from app.models import document
        
        # Uncomment to drop and recreate tables - BE CAREFUL!
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    db = async_session_maker()
    try:
        yield db
    finally:
        await db.close()

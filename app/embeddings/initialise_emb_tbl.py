from langchain_postgres import Column
from sqlalchemy.exc import ProgrammingError
import logging
from app.config import settings
from app.db import pg_engine

logger = logging.getLogger(__name__)

class EmbeddingsTable:
    def __init__(self) -> None:
        pass
    
    @classmethod
    async def create(self):
        try:
            await pg_engine.ainit_vectorstore_table(
                table_name=settings.USERGUIDE_TABLE,
                vector_size=settings.VECTOR_SIZE,
                schema_name=settings.USERGUIDE_SCHEMA,
                overwrite_existing=settings.OVERWRITE,
                metadata_columns=[
                    Column("headingTrace", "TEXT"),
                    Column("pageTrace", "TEXT"),
                    Column("page_id", "TEXT"),
                    Column("section_id", "TEXT"),
                ],
            )
        except ProgrammingError as e:
            # Catching the exception here
            logger.info("Table already exists. Skipping creation.")        
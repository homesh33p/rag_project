from langchain_postgres import Column
from sqlalchemy.exc import ProgrammingError
from app.config import settings
from app.db import pg_engine

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
            print("Table already exists. Skipping creation.")        
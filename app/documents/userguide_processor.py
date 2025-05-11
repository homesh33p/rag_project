"""
Simplified CSV Processing with pgvector
No SQLAlchemy model required - LangChain handles table creation
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres import PGVectorStore
from app.config import settings
from app.db import pg_engine
from .csv_parser import CSVParser

class SimplifiedUserGuideProcessor(CSVParser):

    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = SimplifiedUserGuideProcessor()
        return cls._instance
    
    def __init__(self, model_name=None,*args,**kwargs):
        
        super().__init__(*args,**kwargs)
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            cache_folder=settings.MODEL_CACHE_DIR
        )
        
        # Connection string from config
        self.connection_string = settings.DATABASE_URL

    async def process_csv_to_vectorstore(self):
        """Process CSV and store directly in pgvector."""
        
        # 1. Read CSV
        documents = self._load_documents_from_csv()
        
        self.vectorstore = await PGVectorStore.create(
            engine=pg_engine,
            schema_name=settings.USERGUIDE_SCHEMA,
            table_name=settings.USERGUIDE_TABLE,
            embedding_service=self.embeddings,
            metadata_columns=["headingTrace", "pageTrace","page_id","section_id"]
        )        

        await self.vectorstore.aadd_documents(documents=documents)        
        
        return self.vectorstore


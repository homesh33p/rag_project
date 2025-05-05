"""
Simplified CSV Processing with pgvector
No SQLAlchemy model required - LangChain handles table creation
"""

from typing import List, Dict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document
import csv
import os
from dotenv import load_dotenv

class SimplifiedUserGuideProcessor:
    def __init__(self, model_name="all-mpnet-base-v2"):
        load_dotenv()
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        
        # Connection string for pgvector
        self.connection_string = f"postgresql+psycopg2://{os.getenv('RAG_USER')}:{os.getenv('RAG_PASSWORD')}@localhost:5432/rag"

        # Connect to existing vectorstore
        self.vectorstore = PGVector(
            embedding_function=self.embeddings,
            collection_name="userguide",
            connection_string=self.connection_string
        )        
    
    def process_csv_to_vectorstore(self, csv_path: str, collection_name: str = "userguide"):
        """Process CSV and store directly in pgvector."""
        
        # 1. Read CSV
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            csv_data = list(reader)
        
        # 2. Convert to Documents
        documents = []
        for row in csv_data:
            content = row.get('content') or row.get('enhancedContent')
            if content:
                doc = Document(
                    page_content=content,
                    metadata={
                        'headingTrace': row.get('headingTrace', ''),
                        'pageTrace': row.get('pageTrace', ''),
                        'page_id': row.get('page_id', ''),
                        'section_id': row.get('section_id', ''),
                        'source': 'userguide_v1'
                    }
                )
                documents.append(doc)
        
        # 3. Store in pgvector - LangChain creates tables automatically
        vectorstore = PGVector.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=collection_name,
            connection_string=self.connection_string,
            pre_delete_collection=False  # True to overwrite existing data
        )
        
        return vectorstore


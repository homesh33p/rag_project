from ..config import settings
from langchain_community.retrievers import TFIDFRetriever
from langchain_core.documents import Document
import pickle
import os
from .csv_parser import CSVParser

class PersistentTFIDFProcessor(CSVParser):
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = PersistentTFIDFProcessor()
        return cls._instance
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.tfidf_retriever = None
        self.tfidf_path = settings.TFIDF_CACHE_PATH
        
    def initialize(self, csv_path="app/embeddings/userguide_v1.csv", force_rebuild=False):
        """Initialize the TF-IDF retriever - either load from disk or build new"""
        # Try to load existing model if it exists and not forcing rebuild
        if os.path.exists(self.tfidf_path) and not force_rebuild:
            try:
                with open(self.tfidf_path, 'rb') as f:
                    self.tfidf_retriever = pickle.load(f)
                return self.tfidf_retriever
            except Exception as e:
                print(f"Error loading TF-IDF model, rebuilding: {e}")
        
        # Build new model
        print("Building TF-IDF retriever...")
        documents = self._load_documents_from_csv(csv_path)
        self.tfidf_retriever = TFIDFRetriever.from_documents(documents)
        
        # Save to disk for future use
        os.makedirs(os.path.dirname(self.tfidf_path), exist_ok=True)
        with open(self.tfidf_path, 'wb') as f:
            pickle.dump(self.tfidf_retriever, f)
            
        return self.tfidf_retriever
    
    def search(self, query, k=3):
        """Search documents using TF-IDF retrieval"""
        if not self.tfidf_retriever:
            raise ValueError("TF-IDF retriever not initialized. Call initialize() first.")
        
        self.tfidf_retriever.k = k
        results = self.tfidf_retriever.invoke(query)
        
        return results
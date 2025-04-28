from langchain_community.vectorstores.pgvector import PGVector, DistanceStrategy
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DataFrameLoader, CSVLoader
from langchain_community.retrievers import TFIDFRetriever
import pandas as pd
import os
from urllib.parse import quote_plus
import configparser
from typing import List, Dict, Tuple, Any, Optional

class VectorEmbeddingStore:
    """
    Class to handle vector embeddings storage and retrieval for user guide and metadata search.
    """
    def __init__(self, config_path: str = None):
        """Initialize the vector embedding store with configuration."""
        self.config = self._load_config(config_path)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
        self.connection_string = self._get_connection_string()
        
    def _load_config(self, config_path: Optional[str]) -> configparser.ConfigParser:
        """Load configuration from file or use default values."""
        config = configparser.ConfigParser()
        if config_path and os.path.exists(config_path):
            config.read(config_path)
        else:
            # Default configuration - replace with your own defaults
            config["pg_vector_details"] = {
                "host": "localhost",
                "port": "5432",
                "database": "vector_db",
                "user": "postgres",
                "password": "password",
                "CONNECTION_STRING": "postgresql://%s:%s@%s:%s/%s?sslmode=require"
            }
        return config
    
    def _get_connection_string(self) -> str:
        """Create connection string from configuration."""
        if "CONNECTION_STRING" in self.config["pg_vector_details"]:
            connection_string = self.config.get("pg_vector_details", "CONNECTION_STRING") % quote_plus(
                self.config.get("pg_vector_details", "password"))
        else:
            # Build connection string from individual components
            host = self.config.get("pg_vector_details", "host")
            port = self.config.get("pg_vector_details", "port")
            database = self.config.get("pg_vector_details", "database")
            user = self.config.get("pg_vector_details", "user")
            password = quote_plus(self.config.get("pg_vector_details", "password"))
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"
        
        return connection_string
    
    def create_vector_table(self, 
                           filename: str, 
                           page_content_column: str = None, 
                           collection_name: str = "default_collection") -> None:
        """
        Create a vector table in PostgreSQL from a CSV file.
        
        Args:
            filename: Path to CSV file to load
            page_content_column: Column name to use for document content
            collection_name: Name for the vector collection
        """
        try:
            # Load documents from CSV
            if page_content_column:
                df = pd.read_csv(filename)
                loader = DataFrameLoader(df, page_content_column=page_content_column)
            else:
                loader = CSVLoader(filename, encoding="utf-8-sig")
                
            docs = loader.load()
            
            # Create vector store
            PGVector.from_documents(
                documents=docs,
                embedding=self.embeddings,
                collection_name=collection_name,
                distance_strategy=DistanceStrategy.COSINE,
                connection_string=self.connection_string,
                pre_delete_collection=True  # Overwrite if collection exists
            )
            
            print(f"Vector table created for {filename} with collection name: {collection_name}")
        except Exception as e:
            print(f"Error creating vector table: {str(e)}")
            raise
    
    def hybrid_search(self, query: str, collection_name: str, k: int = 5) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Perform hybrid search using both vector similarity and TF-IDF.
        
        Args:
            query: Query string to search for
            collection_name: Name of the vector collection to search
            k: Number of results to return
            
        Returns:
            Tuple containing (simple_context, context_with_metadata)
        """
        try:
            # Load embeddings for vector search
            store = PGVector(
                collection_name=collection_name,
                connection_string=self.connection_string,
                embedding_function=self.embeddings
            )
            
            # Perform vector similarity search
            vector_results = store.similarity_search_with_score(query=query, k=k)
            
            # Read the original CSV for TF-IDF search
            csv_path = f"./db_scripts/{collection_name}.csv"
            if collection_name == "userguide":
                df = pd.read_csv(csv_path, 
                               usecols=["headingTrace", "pageTrace", "page_id", "section_id", "enhancedContent"])
                content_column = "enhancedContent"
            else:
                df = pd.read_csv(csv_path)
                content_column = "Input" if "Input" in df.columns else df.columns[0]
                
            # Create TF-IDF retriever
            loader = DataFrameLoader(df, page_content_column=content_column)
            documents = loader.load_and_split()
            tfidf_retriever = TFIDFRetriever.from_documents(documents)
            tfidf_retriever.k = k
            tfidf_results = tfidf_retriever.invoke(query)
            
            # Combine and deduplicate results
            related_contents = []
            context_list = []
            related_contents_with_metadata = []
            
            # Process vector search results
            for doc, score in vector_results:
                if str(doc.page_content) not in context_list:
                    contents = {
                        'pageID': doc.metadata.get('page_id', ''),
                        'sectionID': doc.metadata.get('section_id', ''),
                        'content': str(doc.page_content)
                    }
                    related_contents.append(contents)
                    context_list.append(str(doc.page_content))
                    
                    # Include additional metadata if available
                    contents_with_meta = contents.copy()
                    if 'pageTrace' in doc.metadata and 'headingTrace' in doc.metadata:
                        contents_with_meta.update({
                            "pageTrace": doc.metadata['pageTrace'],
                            'headingTrace': doc.metadata['headingTrace']
                        })
                    related_contents_with_metadata.append(contents_with_meta)
            
            # Process TF-IDF results
            for doc in tfidf_results:
                if str(doc.page_content) not in context_list:
                    contents = {
                        'pageID': doc.metadata.get('page_id', ''),
                        'sectionID': doc.metadata.get('section_id', ''),
                        'content': str(doc.page_content)
                    }
                    related_contents.append(contents)
                    context_list.append(str(doc.page_content))
                    
                    # Include additional metadata if available
                    contents_with_meta = contents.copy()
                    if 'pageTrace' in doc.metadata and 'headingTrace' in doc.metadata:
                        contents_with_meta.update({
                            "pageTrace": doc.metadata['pageTrace'],
                            'headingTrace': doc.metadata['headingTrace']
                        })
                    related_contents_with_metadata.append(contents_with_meta)
            
            return related_contents, related_contents_with_metadata
            
        except Exception as e:
            print(f"Error in hybrid search: {str(e)}")
            return [], []


# Example usage
if __name__ == "__main__":
    # Initialize the vector store
    vector_store = VectorEmbeddingStore()
    
    # Create tables for user guide and metadata search
    vector_store.create_vector_table(
        filename="db_scripts/userguide.csv",
        page_content_column="enhancedContent",
        collection_name="userguide"
    )
    
    vector_store.create_vector_table(
        filename="db_scripts/metadatasearch.csv",
        page_content_column="Input",
        collection_name="metadatasearch"
    )
    
    # Example search
    query = "How do I create a new dashboard?"
    results, results_with_metadata = vector_store.hybrid_search(
        query=query,
        collection_name="userguide",
        k=5
    )
    
    print(f"Found {len(results)} results for query: '{query}'")
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Page ID: {result['pageID']}")
        print(f"Section ID: {result['sectionID']}")
        print(f"Content excerpt: {result['content'][:100]}...")
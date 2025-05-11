# app/config.py

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # For starting postgres root password is needed
    # If supplied will be used to start postgres if not running
    ROOT_PASSWORD: str = os.getenv("ROOT_PASSWORD", "")

    # Database settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "your_postgres_password")
    RAG_USER: str = os.getenv("RAG_USER", "raguser")
    RAG_PASSWORD: str = os.getenv("RAG_PASSWORD", "ragpass")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"postgresql+asyncpg://{RAG_USER}:{RAG_PASSWORD}@localhost:5432/rag")
    
    # Application settings
    APP_NAME: str = "RAG API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Vector embedding settings
    EMBEDDING_MODEL: str = "all-mpnet-base-v2"
    CACHE_DIR: str = "app/cache"
    MODEL_CACHE_DIR: str = f"{CACHE_DIR}/models"
    EMBEDDING_CACHE_DIR: str = f"{CACHE_DIR}/embeddings"
    TFIDF_CACHE_PATH: str = f"{CACHE_DIR}/tfidf_retriever.pkl"
    
    CSV_VERSION:str = "1"
    USERGUIDE_SCHEMA: str = os.getenv("USERGUIDE_SCHEMA", "userguide")
    CUSTOM_SCHEMA: str = os.getenv("CUSTOM_SCHEMA", "custom_documents")
    USERGUIDE_TABLE:str = "USERGUIDE"+"_v"+CSV_VERSION
    VECTOR_SIZE:int= 768 # this is for all-mpnet-base-v2 model
    OVERWRITE:bool = True    

    # API settings
    MAX_RESULTS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
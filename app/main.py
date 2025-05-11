from fastapi import FastAPI
import os
import subprocess
import sys
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, query
from contextlib import asynccontextmanager
from app.db import init_db, engine, pg_engine
from app.documents.tfidf_processor import PersistentTFIDFProcessor
from app.documents.userguide_processor import SimplifiedUserGuideProcessor


def check_postgres_running():
    """Check if PostgreSQL server is running"""
    try:
        result = subprocess.run(
            ["pg_isready"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def start_postgres():
    """Start PostgreSQL server if not running"""
    print("PostgreSQL is not running. Attempting to start...")
    try:
        result = subprocess.run(
            ["sudo", "-S", "service", "postgresql", "start"],
            input=f"{settings.ROOT_PASSWORD}\n",
            text=True,
            capture_output=True
        )
        if result.returncode == 0:
            print("PostgreSQL server started successfully")
            return True
        else:
            print(f"Failed to start PostgreSQL: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error starting PostgreSQL: {str(e)}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create cache directories if they don't exist
    os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
    os.makedirs(settings.EMBEDDING_CACHE_DIR, exist_ok=True)

    # Set environment variable for Hugging Face cache
    os.environ["HF_HOME"] = settings.MODEL_CACHE_DIR

    # Check if PostgreSQL is running and start if needed
    if not check_postgres_running():
        if not start_postgres():
            print("Could not start PostgreSQL server. Exiting...")
            sys.exit(1)

    # Startup: Initialize resources
    await init_db()

    # Initialize TF-IDF retriever
    tfidf_processor = PersistentTFIDFProcessor.get_instance()
    tfidf_processor.initialize()

    # Initialize vector store
    # The constructor already sets up the connection
    simplified_ug_processor = SimplifiedUserGuideProcessor.get_instance()
    await simplified_ug_processor.process_csv_to_vectorstore()

    print("Resources initialized, application ready")

    yield  # Application runs here

    # Shutdown: Clean up resources
    print("Shutting down and cleaning up resources")
    
    # Clean up resources
    # Release the vector store connections
    simplified_ug_processor = SimplifiedUserGuideProcessor.get_instance()
    if hasattr(simplified_ug_processor, 'vectorstore') and simplified_ug_processor.vectorstore:
        # Access the underlying engine to close it
        await simplified_ug_processor.vectorstore._engine.close()
    
    # Clean up any engine connections
    await pg_engine.close()
    await engine.dispose()
    

app = FastAPI(
    title=settings.APP_NAME,
    description="Retrieval Augmented Generation API with pgvector",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Rest of your app configuration remains the same
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API"}


app.include_router(documents.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")

# RAG Project with FastAPI and pgvector

A Retrieval Augmented Generation (RAG) API built with FastAPI and pgvector for efficient vector similarity search.

## Features

- Document storage and retrieval with vector embeddings
- Semantic search using pgvector
- RESTful API with FastAPI
- PostgreSQL with pgvector extension for vector operations
- Alembic for database migrations

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL with pgvector extension installed

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example`
5. Initialize the database:
   ```
   alembic upgrade head
   ```

### Running the Application

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with pytest:

```
pytest
```

To run a specific test:

```
pytest tests/test_documents.py::test_create_document -v
```

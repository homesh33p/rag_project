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

## [Project Documentation](./project_ref_docs/index.md)

## Additional explanation

1. Data Loading:
    - Content is stored in userguide.csv with fields: headingTrace, pageTrace, page_id, section_id,
  content, and enhancedContent
  2. Vector Database Storage:
    - When the application runs, the content is loaded into PGVector (PostgreSQL with vector extensions)
    - Text is embedded using the all-mpnet-base-v2 model for semantic search
  3. Query Processing:
    - User questions are analyzed using two methods:
        - TF-IDF retrieval (keyword matching)
      - Vector similarity search (semantic matching)
    - Both approaches are combined to retrieve the most relevant documentation
  4. Response Generation:
    - The system finds the best matching documentation sections
    - Uses a language model to generate a helpful response based on the retrieved context
    - Formats the response with "Learn more" links to related sections
    - Returns a structured JSON object with the answer and optional secondary links

  Integration with Main System:

  - User questions are routed to the User Guide executor via the Router module
  - The system uses it as a fallback for unclassified questions
  - It's fully integrated with the conversation management system to maintain context
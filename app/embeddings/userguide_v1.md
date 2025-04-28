# RAG System User Guide

## Introduction

The RAG (Retrieval Augmented Generation) System is a powerful tool that combines document storage, vector search, and API functionality to enable semantic search capabilities for your applications. This user guide provides comprehensive information on how to use the system effectively.

The RAG System offers the following key features:
- Document storage with vector embeddings
- Semantic search using pgvector
- RESTful API with FastAPI
- Efficient retrieval of contextually relevant information

This guide will walk you through:
- System setup and installation
- API endpoints and usage
- Query construction
- Best practices for optimal results

Before getting started, ensure you have the necessary prerequisites:
- Python 3.8+
- PostgreSQL with pgvector extension
- Basic understanding of REST APIs

The system is designed to be easy to use while providing powerful semantic search capabilities. By following this guide, you'll be able to quickly integrate the RAG System into your applications and leverage its full potential.

## Getting Started

### Installation

Setting up the RAG System involves installing the necessary components and configuring the environment. Follow these steps to get started:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rag-system.git
   cd rag-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables by creating a .env file based on .env.example:
   ```
   # PostgreSQL admin credentials
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_postgres_password

   # RAG database user credentials
   RAG_USER=raguser
   RAG_PASSWORD=ragpass
   ```

5. Run the database setup script:
   ```bash
   ./setup.sh
   ```
   This script will:
   - Install the pgvector extension
   - Create a new database called 'rag'
   - Create a user with appropriate permissions
   - Enable the vector extension in the database

6. Apply database migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

After completing these steps, the API will be available at http://localhost:8000.

You can verify the installation by accessing the API documentation at http://localhost:8000/docs or by sending a GET request to http://localhost:8000/ which should return a welcome message.

> **Note**: For production deployments, you should use a proper web server like Gunicorn behind a reverse proxy such as Nginx, with appropriate security measures.

## API Reference

### API Endpoints

The RAG System provides several API endpoints for interacting with the system. Here's a comprehensive list of available endpoints and their functionalities:

#### 1. Root Endpoint
- **URL**: GET /
- **Description**: Returns a welcome message and confirms the API is running
- **Response**: `{"message": "Welcome to the RAG API"}`

#### 2. Document Management
- **Create Document**:
  - **URL**: POST /api/v1/documents
  - **Description**: Creates a new document in the database
  - **Request Body**: `{"title": "Document Title", "content": "Document content..."}`
  - **Response**: Document object with id, title, content, created_at, and updated_at fields

- **List Documents**:
  - **URL**: GET /api/v1/documents
  - **Description**: Returns a list of documents
  - **Query Parameters**: skip (default: 0), limit (default: 10)
  - **Response**: Array of document objects

- **Get Document**:
  - **URL**: GET /api/v1/documents/{document_id}
  - **Description**: Retrieves a specific document by ID
  - **Path Parameters**: document_id (integer)
  - **Response**: Document object
  - **Error**: 404 if document not found

#### 3. Query Functionality
- **Search Documents**:
  - **URL**: POST /api/v1/query
  - **Description**: Performs semantic search on documents
  - **Request Body**: `{"query": "Your search query", "top_k": 3}`
  - **Response**: Array of document objects with similarity scores
  - **Note**: The top_k parameter controls the number of results returned (default: 3, max: 10)

All API responses are in JSON format. For detailed schema information, refer to the OpenAPI documentation available at /docs when the server is running.

Examples of using the API with curl:

1. Create a document:
```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
     -H "Content-Type: application/json" \
     -d '{"title": "Vector Databases", "content": "Vector databases are designed for efficient similarity search in high-dimensional spaces."}'
```

2. Query documents:
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "How do vector databases work?", "top_k": 5}'
```

## Core Functionality

### Document Storage

The Document Storage functionality allows you to store text documents in the system for later retrieval. When a document is stored, it is automatically converted into a vector embedding that captures its semantic meaning, enabling similarity-based search.

#### Key aspects of document storage:

1. **Document Structure**
   
   Each document consists of:
   - **Title**: A descriptive name for the document (required)
   - **Content**: The main text body of the document (required)
   - **Embedding**: Vector representation of the content (automatically generated)
   - **Created/Updated timestamps**: Automatically managed by the system

2. **Adding Documents**
   
   To add a document to the system:
   
   a. Using the API directly:
   ```
   POST /api/v1/documents
   Content-Type: application/json
   
   {
     "title": "Understanding Vector Embeddings",
     "content": "Vector embeddings are numerical representations of data that capture semantic relationships..."
   }
   ```
   
   b. Using Python with requests:
   ```python
   import requests
   
   response = requests.post(
       "http://localhost:8000/api/v1/documents",
       json={
           "title": "Understanding Vector Embeddings",
           "content": "Vector embeddings are numerical representations of data that capture semantic relationships..."
       }
   )
   document = response.json()
   print(f"Document created with ID: {document['id']}")
   ```

3. **Document Size Considerations**
   - The system is optimized for text documents ranging from a few sentences to several paragraphs
   - Very large documents (>100KB) may be automatically split into smaller chunks
   - For optimal search results, consider splitting very large documents into logical sections

4. **Embedding Generation**
   
   When a document is stored, the system:
   - Preprocesses the text (cleaning, normalization)
   - Generates a vector embedding using the all-mpnet-base-v2 model
   - Stores both the original text and the vector representation
   - The embedding process is automatic and transparent to the user

**Best Practices**:
- Store logically coherent chunks of information for better retrieval results
- Include relevant titles that summarize the document content
- For CSV or tabular data, consider storing each row or logical section as a separate document
- Update documents when information changes to ensure embeddings remain current

### Semantic Search

Semantic search is the core functionality of the RAG System, allowing you to find documents based on their meaning rather than just keyword matching. This capability is powered by vector embeddings and similarity metrics.

#### How Semantic Search Works:

1. **Query Processing**
   - When you submit a search query, the system converts it into a vector embedding using the same model used for document storage
   - This query vector captures the semantic meaning of your question or search terms
   - The system then compares this vector against all document vectors in the database

2. **Similarity Calculation**
   - The system uses cosine similarity as the primary metric to compare vectors
   - Cosine similarity measures the angle between vectors, ranging from -1 (opposite meaning) to 1 (identical meaning)
   - Documents with higher similarity scores are more semantically related to your query

3. **Result Ranking**
   - Results are ranked by similarity score in descending order
   - The top_k parameter controls how many results are returned
   - Each result includes the document content and a similarity score

4. **Using Semantic Search**
   
   To search for documents:
   
   a. Using the API directly:
   ```
   POST /api/v1/query
   Content-Type: application/json
   
   {
     "query": "What are the benefits of vector databases?",
     "top_k": 3
   }
   ```
   
   b. Using Python with requests:
   ```python
   import requests
   
   response = requests.post(
       "http://localhost:8000/api/v1/query",
       json={
           "query": "What are the benefits of vector databases?",
           "top_k": 5
       }
   )
   results = response.json()
   for i, doc in enumerate(results):
       print(f"Result {i+1}: {doc['title']} (Similarity: {doc.get('similarity', 'N/A')})")
       print(f"Content: {doc['content'][:100]}...")
   ```

5. **Query Formulation Tips**
   - Be specific: Clearly articulate what you're looking for
   - Use natural language: The system understands conversational queries
   - Provide context: Include relevant details for more accurate results
   - Try variations: If you don't get desired results, try rephrasing your query

6. **Understanding Results**
   - Similarity scores above 0.8 generally indicate high relevance
   - Scores between 0.6-0.8 indicate moderate relevance
   - Scores below 0.6 may be tangentially related but less relevant
   - An empty result list means no documents matched well with your query

The semantic search capability allows you to find information based on conceptual understanding rather than exact keyword matches, making it powerful for retrieving relevant information even when the exact terminology differs.

## Advanced Features

### Bulk Document Upload

The RAG System supports bulk document upload for efficiently adding multiple documents to the database. This feature is particularly useful when migrating existing document collections or processing large datasets.

#### Bulk Upload Methods:

1. **Using CSV Files**
   
   You can upload multiple documents from a CSV file with the following structure:
   
   a. Required CSV Format:
   ```
   title,content
   "Document 1 Title","Document 1 content text goes here..."
   "Document 2 Title","Document 2 content text goes here..."
   ```
   
   b. Processing the CSV with Python:
   ```python
   import csv
   import requests
   
   def upload_csv_documents(csv_path, api_url):
       with open(csv_path, 'r', encoding='utf-8') as file:
           reader = csv.DictReader(file)
           success_count = 0
           failure_count = 0
           
           for row in reader:
               response = requests.post(
                   f"{api_url}/api/v1/documents",
                   json={
                       "title": row["title"],
                       "content": row["content"]
                   }
               )
               
               if response.status_code == 201:
                   success_count += 1
               else:
                   failure_count += 1
                   print(f"Failed to upload: {row['title']}")
           
           print(f"Upload complete. Success: {success_count}, Failures: {failure_count}")
   
   # Example usage
   upload_csv_documents("documents.csv", "http://localhost:8000")
   ```

2. **Using the Batch API**
   
   For very large document collections, the system provides a batch processing endpoint:
   
   a. Batch Request Format:
   ```
   POST /api/v1/documents/batch
   Content-Type: application/json
   
   {
     "documents": [
       {
         "title": "Document 1 Title",
         "content": "Document 1 content..."
       },
       {
         "title": "Document 2 Title",
         "content": "Document 2 content..."
       }
     ]
   }
   ```
   
   b. Response Format:
   ```json
   {
     "success_count": 2,
     "failure_count": 0,
     "total": 2,
     "failed_documents": []
   }
   ```

3. **Processing Structured Documents**
   
   When uploading structured documents like technical manuals or textbooks:
   
   a. Consider splitting by sections:
   - Create a separate document for each logical section
   - Use a consistent title format (e.g., "Chapter 1: Introduction")
   - Include context in content where needed
   
   b. Example preprocessing script:
   ```python
   def preprocess_textbook(file_path, section_delimiter="## "):
       documents = []
       current_title = ""
       current_content = []
       
       with open(file_path, 'r', encoding='utf-8') as file:
           for line in file:
               if line.startswith(section_delimiter):
                   # Save previous section if it exists
                   if current_title and current_content:
                       documents.append({
                           "title": current_title,
                           "content": "\n".join(current_content)
                       })
                   
                   # Start new section
                   current_title = line.strip("#").strip()
                   current_content = []
               else:
                   current_content.append(line)
       
       # Add the last section
       if current_title and current_content:
           documents.append({
               "title": current_title,
               "content": "\n".join(current_content)
           })
       
       return documents
   ```

**Best Practices for Bulk Upload**:
- Process large uploads in batches of 100-500 documents
- Implement error handling and retry logic for failed uploads
- Ensure document titles are unique or include identifiers
- Monitor database performance during large uploads
- Consider running bulk uploads during off-peak hours
- Validate document content before upload to ensure quality
- Include preprocessing steps to clean and normalize text

> **Note**: Very large bulk uploads may temporarily impact query performance while the vector indexes are being updated. Plan uploads accordingly.

## Security

### API Authentication

The RAG System implements API authentication to ensure secure access to the endpoints. This section explains how to authenticate your requests to the API.

#### Authentication Methods:

1. **API Key Authentication**
   
   The primary authentication method uses API keys:
   
   a. Obtaining an API Key:
   - API keys are generated by the system administrator
   - Each key is associated with specific permissions and rate limits
   - Contact your administrator to request a new API key
   
   b. Using API Keys in Requests:
   ```
   GET /api/v1/documents
   X-API-Key: your_api_key_here
   ```
   
   c. API Key in Python Requests:
   ```python
   import requests
   
   api_key = "your_api_key_here"
   headers = {"X-API-Key": api_key}
   
   response = requests.get(
       "http://localhost:8000/api/v1/documents",
       headers=headers
   )
   ```

2. **Environment Configuration**
   
   For development environments, you can configure authentication:
   
   a. In the .env file:
   ```
   # Authentication settings
   AUTH_ENABLED=true
   AUTH_API_KEY=development_key
   ```
   
   b. Disabling authentication (development only):
   ```
   AUTH_ENABLED=false
   ```
   Note: This should never be done in production environments.

3. **Security Best Practices**
   
   When working with API authentication:
   
   - Never share API keys in public repositories or client-side code
   - Implement proper key rotation procedures
   - Use environment variables to store API keys
   - Set appropriate expiration for API keys
   - Implement rate limiting to prevent abuse
   - Monitor API usage for suspicious activity

4. **Error Responses**
   
   When authentication fails, the API returns:
   
   ```json
   {
     "status_code": 401,
     "detail": "Invalid API key",
     "type": "unauthorized"
   }
   ```
   
   Status codes:
   - 401: Invalid or missing API key
   - 403: Valid API key but insufficient permissions
   - 429: Rate limit exceeded

> **Note**: The authentication mechanism is designed to be secure while minimizing overhead. API keys should be treated as sensitive information and protected accordingly.

### Rate Limiting

The RAG System implements rate limiting to prevent abuse, ensure fair usage, and maintain system performance. This section explains how rate limiting works and what to expect when limits are reached.

#### Rate Limiting Implementation:

1. **Default Rate Limits**
   
   The system enforces the following default limits:
   
   - Document creation: 100 requests per hour
   - Document retrieval: 1000 requests per hour
   - Query operations: 500 requests per hour
   
   These limits are applied per API key or IP address.

2. **Rate Limit Headers**
   
   The API includes rate limit information in response headers:
   
   ```
   X-Rate-Limit-Limit: 100
   X-Rate-Limit-Remaining: 95
   X-Rate-Limit-Reset: 1634567890
   ```
   
   - X-Rate-Limit-Limit: The maximum number of requests allowed in the current period
   - X-Rate-Limit-Remaining: The number of requests remaining in the current period
   - X-Rate-Limit-Reset: The time at which the rate limit resets (Unix timestamp)

3. **Handling Rate Limit Errors**
   
   When a rate limit is exceeded, the API returns:
   
   ```json
   {
     "status_code": 429,
     "detail": "Rate limit exceeded. Try again in 45 seconds.",
     "type": "too_many_requests"
   }
   ```
   
   Best practices for handling rate limits:
   
   ```python
   import requests
   import time
   
   def make_request_with_retry(url, method="get", data=None, max_retries=3):
       headers = {"X-API-Key": "your_api_key"}
       retry_count = 0
       
       while retry_count < max_retries:
           response = requests.request(
               method,
               url,
               headers=headers,
               json=data
           )
           
           if response.status_code != 429:
               return response
           
           # Extract retry-after header or use default backoff
           retry_after = int(response.headers.get('Retry-After', 60))
           print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
           time.sleep(retry_after)
           retry_count += 1
       
       return response  # Return the last response if all retries failed
   ```

4. **Requesting Higher Limits**
   
   If you need higher rate limits:
   
   - Contact your system administrator with your use case
   - Provide expected request volume and patterns
   - Consider implementing batching for document operations to reduce request frequency

5. **Best Practices**
   
   To work effectively with rate limits:
   
   - Implement exponential backoff for retries
   - Use batch operations when possible
   - Cache frequently accessed information
   - Monitor your usage to stay within limits
   - Distribute large operations over time
   - Include rate limit handling in your applications

> **Note**: Rate limiting is designed to ensure system stability and fair resource allocation. If you consistently hit rate limits, review your usage patterns or consider requesting adjusted limits for your use case.

## Technical Reference

### Embedding Models

The RAG System uses text embedding models to convert documents and queries into vector representations. Understanding these models can help you optimize your use of the system.

#### About the Default Embedding Model:

1. **Model Information**
   - Name: all-mpnet-base-v2
   - Vector Dimensions: 768
   - Model Type: Sentence Transformer
   - Training Data: Diverse text corpus including web content, books, and research papers
   - Optimization: Tuned for semantic similarity tasks

2. **Embedding Properties**
   - Each document is represented as a 768-dimensional floating-point vector
   - Vectors capture semantic meaning, context, and relationships between concepts
   - Similar concepts have vectors that are close in the vector space
   - The model is language-aware and understands English text well

3. **When Embeddings Are Generated**
   - Document embeddings: Generated at document storage time
   - Query embeddings: Generated when a query is processed
   - The same model is used for both document and query embedding to ensure compatibility

4. **Technical Details**
   - Embedding storage: Vectors are stored using pgvector's native ARRAY(FLOAT) type
   - Distance metric: Cosine similarity (1 - cosine distance) is used by default
   - Preprocessing: Text is normalized, tokenized, and processed through the model

5. **Embedding Limitations**
   - Context window: Limited to approximately 384 tokens (roughly 250-300 words)
   - Language support: Optimized for English, with varying performance on other languages
   - Domain specificity: General-purpose model that may not capture highly specialized terminology

6. **Advanced Usage**
   
   If you're an advanced user integrating with the system:
   
   ```python
   # Example of how embeddings are generated internally
   from sentence_transformers import SentenceTransformer
   
   model = SentenceTransformer('all-mpnet-base-v2')
   embedding = model.encode("Your text here", normalize_embeddings=True)
   # embedding is a numpy array of shape (768,)
   ```

> **Note**: The embedding model is integrated into the system and used automatically. Most users don't need to interact with it directly. This information is provided for those who want to understand the technical underpinnings of the semantic search capability.

### PGVector Configuration

The RAG System uses PostgreSQL with the pgvector extension to store and query vector embeddings. This section covers the technical details of the pgvector configuration.

#### PGVector Database Setup:

1. **Extension Installation**
   
   The pgvector extension must be installed in your PostgreSQL instance:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
   This is handled automatically by the setup script.

2. **Vector Column**
   
   The system uses a dedicated column in the documents table to store vector data:
   ```sql
   CREATE TABLE documents (
       id SERIAL PRIMARY KEY,
       title VARCHAR(255) NOT NULL,
       content TEXT NOT NULL,
       embedding VECTOR(768),  -- 768 dimensions for all-mpnet-base-v2
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE
   );
   ```

3. **Index Types**
   
   PGVector supports several index types for efficient similarity search:
   
   a. IVFFlat (default in the system):
   ```sql
   CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
   ```
   Good for general-purpose similarity search with moderate dataset size.
   
   b. HNSW (for better accuracy but slower indexing):
   ```sql
   CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
   ```
   Better search quality but slower index creation.
   
   c. Flat (for smaller datasets):
   ```sql
   CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);
   ```
   Best for small datasets (under 10,000 documents).

4. **Distance Operators**
   
   PGVector provides three distance metrics:
   - `<->`: Cosine distance (default in the system)
   - `<=>`: Euclidean distance
   - `<#>`: Inner product

5. **Performance Tuning**
   
   For optimal performance:
   - Lists parameter: Set to √n/10 where n is the number of records
   - When using HNSW: Higher m and ef_construction values improve recall at the cost of build time and index size
   - Use LIMIT in queries to restrict the search space

6. **Example Query with PGVector**
   
   This is how the system performs vector similarity search internally:
   ```sql
   SELECT id, title, content, 1 - (embedding <-> $1) as similarity
   FROM documents
   ORDER BY embedding <-> $1
   LIMIT $2;
   ```
   Where $1 is the query vector and $2 is the top_k parameter.

> **Note**: These details are primarily for administrators and advanced users who want to understand or customize the vector database configuration. Regular users interact with the system through the API without needing to understand these technical details.

## Administration

### Performance Optimization

Optimizing the performance of your RAG System ensures efficient operation, faster query responses, and better resource utilization. This section provides guidance on performance tuning for different aspects of the system.

#### Database Optimization:

1. **PGVector Indexing**
   
   Properly configured indexes are critical for vector search performance:
   
   a. Choosing the right index type:
   - For datasets < 10,000 documents: Flat index is sufficient
   - For datasets 10,000 - 1M documents: IVFFlat index with appropriate lists parameter
   - For datasets > 1M documents: Consider HNSW index for better recall/performance tradeoff
   
   b. Index tuning:
   ```sql
   -- For medium datasets (IVFFlat)
   CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
   
   -- For large datasets with high recall requirements (HNSW)
   CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 100);
   ```
   
   c. Optimize lists parameter:
   The lists parameter should typically be √n/10 where n is the number of records.
   
   Example: For 1 million records, use: √1,000,000/10 = 100 lists

2. **Database Configuration**
   
   Adjust PostgreSQL settings for vector operations:
   
   ```
   # Memory settings
   shared_buffers = 4GB             # 25% of system RAM up to 8GB
   work_mem = 128MB                 # Increase for complex vector queries
   maintenance_work_mem = 1GB       # Helps with index creation
   
   # Query planning
   random_page_cost = 1.1           # Lower for SSDs
   effective_cache_size = 12GB      # 75% of system RAM
   
   # Checkpoints
   checkpoint_timeout = 15min       # Reduce I/O impact
   max_wal_size = 4GB               # Larger for busy systems
   ```

3. **Connection Pooling**
   
   Implement connection pooling to reduce connection overhead:
   ```python
   # In database.py
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,               # Adjust based on expected concurrent users
       max_overflow=10,            # Additional connections when pool is full
       pool_timeout=30,            # Seconds to wait for a connection
       pool_recycle=1800,          # Recycle connections after 30 minutes
       echo=False
   )
   ```

#### API Performance:

1. **Query Optimization**
   
   Optimize query processing:
   
   a. Limit results appropriately:
   - Use reasonable top_k values (3-10 for most use cases)
   - Implement pagination for large result sets
   
   b. Caching frequent queries:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   async def cached_query_embedding(query_text: str) -> list[float]:
       # Generate and return embedding
   ```
   
   c. Batch processing:
   - Use batch endpoints for multiple operations
   - Implement bulk document upload for large collections

2. **Application Configuration**
   
   Optimize FastAPI settings:
   
   a. Worker configuration:
   ```bash
   # For production deployment
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
   
   b. Adjust workers based on CPU cores:
   - General guideline: (2 × cores) + 1 workers
   - For 4-core server: 9 workers
   - For 8-core server: 17 workers

3. **Embedding Generation**
   
   Optimize embedding processing:
   
   a. Batch embedding generation:
   - Process documents in batches of 8-32 for efficient GPU utilization
   - Implement parallel processing for CPU-based embedding generation
   
   b. Consider hardware acceleration:
   - GPU acceleration significantly improves embedding generation speed
   - CPU optimization with appropriate batch sizes can help when GPU is unavailable

#### Monitoring and Tuning:

1. **Identify Bottlenecks**
   
   Use monitoring to identify performance issues:
   
   a. Slow query analysis:
   ```sql
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   ```
   
   b. Monitor resource utilization:
   - CPU usage during query processing
   - Memory usage during embedding generation
   - I/O patterns during batch operations

2. **Scaling Strategies**
   
   Implement appropriate scaling:
   
   a. Vertical scaling:
   - Increase memory for larger embedding models
   - Add CPU/GPU resources for faster embedding generation
   - Upgrade storage for larger document collections
   
   b. Horizontal scaling:
   - Implement read replicas for query-heavy workloads
   - Consider sharding for very large document collections
   - Use load balancing for API endpoints

**Best Practices**:
- Start with proper indexes before other optimizations
- Test performance with representative data volumes
- Implement monitoring to track performance metrics
- Optimize the most frequent operations first
- Balance resource usage across components
- Consider query patterns when designing indexes
- Review and adjust optimizations as usage patterns change

> **Note**: Performance optimization should be an iterative process based on actual usage patterns and specific deployment environments.

### Troubleshooting

This section provides guidance for identifying and resolving common issues you might encounter when using the RAG System.

#### Common Issues and Solutions:

1. **API Connection Issues**
   
   Issue: Unable to connect to the API endpoints
   
   Troubleshooting steps:
   - Verify the server is running: `ps aux | grep uvicorn`
   - Check network connectivity: `curl http://localhost:8000/`
   - Verify port availability: `netstat -tuln | grep 8000`
   - Check for firewall blocking: `sudo ufw status`
   
   Solutions:
   - Restart the API server: `systemctl restart rag-api`
   - Check application logs for errors: `tail -f /var/log/rag/application.log`
   - Verify environment variables are correctly set in .env file

2. **Database Connection Problems**
   
   Issue: API reports database connection errors
   
   Troubleshooting steps:
   - Check PostgreSQL is running: `systemctl status postgresql`
   - Verify connection settings: `psql -U raguser -h localhost -d rag`
   - Check for connection limits: `SELECT * FROM pg_stat_activity;`
   
   Solutions:
   - Restart PostgreSQL: `systemctl restart postgresql`
   - Reset connection pool: Restart the API server
   - Check database logs: `tail -f /var/log/postgresql/postgresql-14-main.log`

3. **Vector Search Not Returning Expected Results**
   
   Issue: Query results are not relevant or no results are returned
   
   Troubleshooting steps:
   - Verify documents exist: `SELECT COUNT(*) FROM documents;`
   - Check embeddings are present: `SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL;`
   - Test direct vector comparison in database:
     ```sql
     -- Replace with actual query vector
     WITH query_vector AS (SELECT '[0.1, 0.2, ...]'::vector AS v)
     SELECT id, title, 1 - (embedding <-> v) AS similarity
     FROM documents, query_vector
     ORDER BY similarity DESC
     LIMIT 5;
     ```
   
   Solutions:
   - Reindex vectors if corrupted:
     ```sql
     UPDATE documents SET embedding = NULL WHERE id IN (problem_ids);
     -- Then use your embedding service to regenerate them
     ```
   - Try different query formulations
   - Verify embedding model is working correctly

4. **Slow Query Performance**
   
   Issue: Vector searches take too long to complete
   
   Troubleshooting steps:
   - Check query execution time: 
     ```sql
     EXPLAIN ANALYZE SELECT id FROM documents 
     ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector LIMIT 10;
     ```
   - Verify indexes are being used: `SELECT * FROM pg_indexes WHERE tablename = 'documents';`
   - Check for database load: `SELECT * FROM pg_stat_activity;`
   
   Solutions:
   - Create or optimize indexes:
     ```sql
     CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);
     ```
   - Increase work_mem for vector operations
   - Reduce result set size with appropriate LIMIT
   - Consider query caching for frequent searches

5. **Authentication Failures**
   
   Issue: API returns 401 Unauthorized or 403 Forbidden errors
   
   Troubleshooting steps:
   - Verify API key is correct and not expired
   - Check for typos in the header name: should be `X-API-Key`
   - Verify permissions associated with the API key
   
   Solutions:
   - Request a new API key if needed
   - Check authentication logs: `grep auth /var/log/rag/application.log`
   - Verify the authentication middleware is properly configured

6. **Embedding Generation Issues**
   
   Issue: Document uploads fail during embedding generation
   
   Troubleshooting steps:
   - Check embedding service status
   - Inspect document content for problematic text
   - Check for memory issues during embedding: `dmesg | grep -i kill`
   
   Solutions:
   - Restart embedding service if applicable
   - Break large documents into smaller chunks
   - Increase memory allocation for embedding generation
   - Clean document text of special characters/formatting

7. **System Resource Limitations**
   
   Issue: System performance degrades under load
   
   Troubleshooting steps:
   - Monitor CPU usage: `top` or `htop`
   - Check memory usage: `free -m`
   - Monitor disk I/O: `iostat -x 1`
   
   Solutions:
   - Increase server resources if possible
   - Optimize PostgreSQL configuration for available memory
   - Implement rate limiting to prevent overload
   - Consider horizontal scaling for high-traffic deployments

#### Diagnostic Commands:

1. **System Health Check**
   ```bash
   # Check API status
   curl -s http://localhost:8000/api/v1/status | jq
   
   # Check database connectivity
   psql -U raguser -h localhost -d rag -c "SELECT version();"
   
   # Check vector extension
   psql -U raguser -h localhost -d rag -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
   ```

2. **Database Inspection**
   ```bash
   # Document count
   psql -U raguser -h localhost -d rag -c "SELECT COUNT(*) FROM documents;"
   
   # Check for missing embeddings
   psql -U raguser -h localhost -d rag -c "SELECT COUNT(*) FROM documents WHERE embedding IS NULL;"
   
   # Check index usage
   psql -U raguser -h localhost -d rag -c "SELECT * FROM pg_stat_user_indexes WHERE relname = 'documents';"
   ```

3. **Log Analysis**
   ```bash
   # Check for errors
   grep -i error /var/log/rag/application.log
   
   # Look for slow queries
   grep -i "slow query" /var/log/rag/application.log
   
   # Check authentication issues
   grep -i "auth" /var/log/rag/application.log | grep -i fail
   ```

**When to Seek Support**:
- If you encounter persistent database connection issues
- When vector search consistently returns irrelevant results
- If system performance degrades significantly under normal load
- When seeing unexplained errors in application logs
- If database indexes appear to be corrupted or ineffective
- When authentication fails despite correct credentials

> **Note**: When reporting issues to support, always include relevant logs, error messages, and steps to reproduce the problem. This information significantly accelerates troubleshooting.

### Logging and Monitoring

The RAG System provides comprehensive logging and monitoring capabilities to help track usage, troubleshoot issues, and optimize performance. This section covers how to access and interpret logs and monitoring data.

#### Logging System:

1. **Log Levels and Categories**
   
   The system uses the following log levels:
   
   - ERROR: Critical issues that require immediate attention
   - WARNING: Potential issues that may need investigation
   - INFO: General operational information
   - DEBUG: Detailed information for troubleshooting
   
   Log categories include:
   - api: API endpoint access and processing
   - db: Database operations and queries
   - auth: Authentication and authorization events
   - embed: Embedding generation processes
   - search: Vector search operations
   - system: General system information

2. **Log File Locations**
   
   Logs are stored in the following locations:
   
   - Application logs: /var/log/rag/application.log
   - Error logs: /var/log/rag/error.log
   - Access logs: /var/log/rag/access.log
   
   For containerized deployments, logs are sent to stdout/stderr.

3. **Log Format**
   
   Each log entry follows this format:
   
   ```
   [TIMESTAMP] [LEVEL] [CATEGORY] [REQUEST_ID] Message
   ```
   
   Example:
   ```
   [2023-10-15 14:30:45.123] [INFO] [api] [req-a1b2c3] Processing query with 5 tokens
   ```
   
   The REQUEST_ID allows tracking related operations across multiple log entries.

4. **Monitoring Metrics**
   
   Key metrics collected by the system:
   
   a. Performance Metrics:
   - Query response time (average, p95, p99)
   - Embedding generation time
   - Database operation latency
   - API endpoint response times
   
   b. Usage Metrics:
   - Requests per minute by endpoint
   - Document count by created date
   - Query volume by hour/day
   - Average document size
   
   c. System Metrics:
   - CPU and memory usage
   - Database connection pool usage
   - Disk space utilization
   - Error rate by endpoint

5. **Monitoring Interfaces**
   
   The system exposes metrics through:
   
   a. Prometheus endpoint:
   - URL: /metrics
   - Format: Prometheus text format
   - Authentication: Required
   
   b. Status endpoint:
   - URL: /api/v1/status
   - Format: JSON
   - Authentication: Required
   
   Example status response:
   ```json
   {
     "status": "healthy",
     "version": "1.2.3",
     "uptime": 43200,
     "db_connection": "healthy",
     "document_count": 1250,
     "query_count_24h": 5432
   }
   ```

6. **Setting Up Alerts**
   
   Configure alerts for:
   
   - Error rate exceeding threshold
   - Response time degradation
   - System resource utilization
   - Database connection issues
   - Authentication failures
   - Unexpected query patterns

**Best Practices**:
- Regularly review logs for error patterns
- Set up log rotation to manage disk space
- Use a centralized logging system for multiple instances
- Correlate logs across components for troubleshooting
- Establish baseline metrics for normal operation
- Configure appropriate alert thresholds to avoid alert fatigue

> **Note**: For production deployments, consider integrating with existing logging and monitoring infrastructure such as ELK Stack, Grafana, or cloud provider monitoring services.

## Integration Examples

### API Client Examples

This section provides examples of how to integrate with the RAG System API using different programming languages and frameworks. These examples demonstrate basic operations like document storage and semantic search.

#### Python Client:

1. **Basic API Client**
   ```python
   import requests
   
   class RAGClient:
       def __init__(self, base_url, api_key=None):
           self.base_url = base_url.rstrip('/')
           self.api_key = api_key
           self.headers = {'Content-Type': 'application/json'}
           if api_key:
               self.headers['X-API-Key'] = api_key
       
       def create_document(self, title, content):
           """Store a new document in the RAG system."""
           url = f"{self.base_url}/api/v1/documents"
           payload = {"title": title, "content": content}
           
           response = requests.post(url, json=payload, headers=self.headers)
           response.raise_for_status()
           return response.json()
       
       def query(self, query_text, top_k=3):
           """Query the RAG system for relevant documents."""
           url = f"{self.base_url}/api/v1/query"
           payload = {"query": query_text, "top_k": top_k}
           
           response = requests.post(url, json=payload, headers=self.headers)
           response.raise_for_status()
           return response.json()
       
       def get_document(self, document_id):
           """Retrieve a specific document by ID."""
           url = f"{self.base_url}/api/v1/documents/{document_id}"
           
           response = requests.get(url, headers=self.headers)
           response.raise_for_status()
           return response.json()
       
       def list_documents(self, skip=0, limit=10):
           """List documents with pagination."""
           url = f"{self.base_url}/api/v1/documents"
           params = {"skip": skip, "limit": limit}
           
           response = requests.get(url, params=params, headers=self.headers)
           response.raise_for_status()
           return response.json()
   
   # Example usage
   client = RAGClient("http://localhost:8000", api_key="your_api_key")
   
   # Store a document
   doc = client.create_document(
       "Vector Databases",
       "Vector databases are specialized database systems designed for similarity search."
   )
   print(f"Created document with ID: {doc['id']}")
   
   # Query documents
   results = client.query("How do similarity searches work?", top_k=3)
   for i, result in enumerate(results):
       print(f"Result {i+1}: {result['title']} (Similarity: {result.get('similarity', 'N/A')})")
   ```

2. **Async Python Client (with httpx)**
   ```python
   import httpx
   import asyncio
   
   class AsyncRAGClient:
       def __init__(self, base_url, api_key=None):
           self.base_url = base_url.rstrip('/')
           self.headers = {'Content-Type': 'application/json'}
           if api_key:
               self.headers['X-API-Key'] = api_key
           self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
       
       async def create_document(self, title, content):
           """Store a new document in the RAG system."""
           url = f"{self.base_url}/api/v1/documents"
           payload = {"title": title, "content": content}
           
           response = await self.client.post(url, json=payload)
           response.raise_for_status()
           return response.json()
       
       async def query(self, query_text, top_k=3):
           """Query the RAG system for relevant documents."""
           url = f"{self.base_url}/api/v1/query"
           payload = {"query": query_text, "top_k": top_k}
           
           response = await self.client.post(url, json=payload)
           response.raise_for_status()
           return response.json()
       
       async def close(self):
           """Close the client session."""
           await self.client.aclose()
   
   # Example usage with async/await
   async def main():
       client = AsyncRAGClient("http://localhost:8000", api_key="your_api_key")
       
       try:
           # Store a document
           doc = await client.create_document(
               "Async Programming",
               "Asynchronous programming allows concurrent operations without blocking."
           )
           print(f"Created document with ID: {doc['id']}")
           
           # Query documents
           results = await client.query("How does concurrency work?", top_k=3)
           for i, result in enumerate(results):
               print(f"Result {i+1}: {result['title']}")
       finally:
           await client.close()
   
   # Run the async example
   asyncio.run(main())
   ```

#### JavaScript/Node.js Client:

1. **Node.js Client**
   ```javascript
   const axios = require('axios');
   
   class RAGClient {
     constructor(baseUrl, apiKey = null) {
       this.baseUrl = baseUrl.replace(/\/$/, '');
       this.headers = {'Content-Type': 'application/json'};
       if (apiKey) {
         this.headers['X-API-Key'] = apiKey;
       }
     }
     
     async createDocument(title, content) {
       const url = `${this.baseUrl}/api/v1/documents`;
       const payload = { title, content };
       
       const response = await axios.post(url, payload, { headers: this.headers });
       return response.data;
     }
     
     async query(queryText, topK = 3) {
       const url = `${this.baseUrl}/api/v1/query`;
       const payload = { query: queryText, top_k: topK };
       
       const response = await axios.post(url, payload, { headers: this.headers });
       return response.data;
     }
     
     async getDocument(documentId) {
       const url = `${this.baseUrl}/api/v1/documents/${documentId}`;
       
       const response = await axios.get(url, { headers: this.headers });
       return response.data;
     }
   }
   
   // Example usage
   async function main() {
     const client = new RAGClient('http://localhost:8000', 'your_api_key');
     
     try {
       // Store a document
       const doc = await client.createDocument(
         'JavaScript Integration',
         'Integrating with APIs in JavaScript using promises and async/await.'
       );
       console.log(`Created document with ID: ${doc.id}`);
       
       // Query documents
       const results = await client.query('How to use async/await with APIs?', 3);
       results.forEach((result, index) => {
         console.log(`Result ${index+1}: ${result.title} (Similarity: ${result.similarity || 'N/A'})`);
       });
     } catch (error) {
       console.error('Error:', error.response ? error.response.data : error.message);
     }
   }
   
   main();
   ```

2. **Browser JavaScript Client**
   ```javascript
   class RAGClient {
     constructor(baseUrl, apiKey = null) {
       this.baseUrl = baseUrl.replace(/\/$/, '');
       this.headers = {'Content-Type': 'application/json'};
       if (apiKey) {
         this.headers['X-API-Key'] = apiKey;
       }
     }
     
     async createDocument(title, content) {
       const url = `${this.baseUrl}/api/v1/documents`;
       const payload = { title, content };
       
       const response = await fetch(url, {
         method: 'POST',
         headers: this.headers,
         body: JSON.stringify(payload)
       });
       
       if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
       }
       return await response.json();
     }
     
     async query(queryText, topK = 3) {
       const url = `${this.baseUrl}/api/v1/query`;
       const payload = { query: queryText, top_k: topK };
       
       const response = await fetch(url, {
         method: 'POST',
         headers: this.headers,
         body: JSON.stringify(payload)
       });
       
       if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
       }
       return await response.json();
     }
   }
   
   // Example usage in browser
   const client = new RAGClient('http://localhost:8000', 'your_api_key');
   
   // Search button click handler
   document.getElementById('search-button').addEventListener('click', async () => {
     const query = document.getElementById('search-input').value;
     const resultsContainer = document.getElementById('search-results');
     
     try {
       resultsContainer.innerHTML = '<p>Searching...</p>';
       const results = await client.query(query, 5);
       
       if (results.length === 0) {
         resultsContainer.innerHTML = '<p>No results found.</p>';
         return;
       }
       
       let html = '<ul>';
       results.forEach(result => {
         html += `
           <li>
             <h3>${result.title}</h3>
             <p>${result.content.substring(0, 200)}...</p>
             <small>Similarity: ${(result.similarity * 100).toFixed(2)}%</small>
           </li>
         `;
       });
       html += '</ul>';
       
       resultsContainer.innerHTML = html;
     } catch (error) {
       resultsContainer.innerHTML = `<p>Error: ${error.message}</p>`;
     }
   });
   ```

#### Application Integration Patterns:

1. **Web Application Integration**
   
   For web applications, implement the following pattern:
   
   ```javascript
   // Frontend search component
   async function searchDocuments(query) {
     // Show loading state
     setLoading(true);
     
     try {
       // Call backend API that wraps the RAG system
       const response = await fetch('/api/search', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ query, limit: 5 })
       });
       
       const results = await response.json();
       
       // Process and display results
       displayResults(results);
     } catch (error) {
       // Handle errors
       showErrorMessage(error.message);
     } finally {
       setLoading(false);
     }
   }
   
   // Backend API route (Node.js/Express example)
   app.post('/api/search', async (req, res) => {
     const { query, limit } = req.body;
     
     try {
       // Your server keeps the API key secure
       const client = new RAGClient('http://rag-api-server:8000', process.env.RAG_API_KEY);
       const results = await client.query(query, limit || 3);
       
       // Optionally transform or enrich results before sending to client
       const processedResults = results.map(doc => ({
         id: doc.id,
         title: doc.title,
         snippet: doc.content.substring(0, 200) + '...',
         relevance: Math.round(doc.similarity * 100)
       }));
       
       res.json(processedResults);
     } catch (error) {
       console.error('RAG search error:', error);
       res.status(500).json({ error: 'Search failed', message: error.message });
     }
   });
   ```

2. **Command Line Interface**
   
   Example of a simple CLI for interacting with the RAG system:
   
   ```python
   #!/usr/bin/env python3
   import argparse
   import json
   import sys
   from ragclient import RAGClient
   
   def main():
       parser = argparse.ArgumentParser(description='RAG System CLI')
       parser.add_argument('--url', default='http://localhost:8000', help='RAG API URL')
       parser.add_argument('--key', help='API Key')
       
       subparsers = parser.add_subparsers(dest='command', help='Command')
       
       # Search command
       search_parser = subparsers.add_parser('search', help='Search documents')
       search_parser.add_argument('query', help='Search query')
       search_parser.add_argument('--limit', type=int, default=3, help='Maximum results')
       search_parser.add_argument('--json', action='store_true', help='Output as JSON')
       
       # Add command
       add_parser = subparsers.add_parser('add', help='Add a document')
       add_parser.add_argument('--title', required=True, help='Document title')
       add_parser.add_argument('--content', help='Document content')
       add_parser.add_argument('--file', help='Read content from file')
       
       # List command
       list_parser = subparsers.add_parser('list', help='List documents')
       list_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
       list_parser.add_argument('--skip', type=int, default=0, help='Skip records')
       
       args = parser.parse_args()
       
       if not args.command:
           parser.print_help()
           return
       
       # Create client
       client = RAGClient(args.url, args.key)
       
       # Handle commands
       if args.command == 'search':
           results = client.query(args.query, args.limit)
           if args.json:
               print(json.dumps(results, indent=2))
           else:
               print(f"Found {len(results)} results for '{args.query}':\n")
               for i, doc in enumerate(results):
                   print(f"[{i+1}] {doc['title']} (Score: {doc.get('similarity', 'N/A'):.2f})")
                   print(f"    {doc['content'][:200]}...")
                   print()
       
       elif args.command == 'add':
           if args.file:
               with open(args.file, 'r') as f:
                   content = f.read()
           elif args.content:
               content = args.content
           else:
               content = sys.stdin.read()
           
           doc = client.create_document(args.title, content)
           print(f"Document created with ID: {doc['id']}")
       
       elif args.command == 'list':
           docs = client.list_documents(args.skip, args.limit)
           print(f"Listing documents ({len(docs)} results):\n")
           for i, doc in enumerate(docs):
               print(f"[{i+1}] ID: {doc['id']}")
               print(f"    Title: {doc['title']}")
               print(f"    Created: {doc['created_at']}")
               print()
   
   if __name__ == '__main__':
       main()
   ```

**Best Practices for Integration**:
- Implement proper error handling and retries
- Cache frequently accessed results when appropriate
- Use connection pooling for backend integrations
- Implement rate limiting protection in clients
- Keep API keys secure and never expose them in client-side code
- Provide user-friendly error messages
- Consider implementing a facade/proxy API for frontend applications
- Add observability through logging and performance monitoring

> **Note**: When integrating with web applications, always keep API keys on the server side and implement a backend proxy to make requests to the RAG API to maintain security.

## Conclusion

The RAG System provides a powerful platform for semantic document search and retrieval using vector embeddings and natural language processing. By following the guidelines in this user guide, you can effectively integrate, optimize, and maintain your RAG deployment.

### Key Takeaways:

1. **Vector Search Capabilities**
   - The system leverages pgvector for efficient similarity search
   - Document content is automatically converted to vector embeddings
   - Semantic search allows finding conceptually similar documents

2. **Integration Options**
   - RESTful API for easy integration with various platforms
   - Client libraries available for common programming languages
   - Batch operations for efficient processing of large document collections

3. **Performance Considerations**
   - Proper indexing is critical for search performance
   - Database configuration should be tuned for vector operations
   - Monitoring and logging help identify optimization opportunities

4. **Security Features**
   - API key authentication controls access
   - Rate limiting prevents abuse
   - Proper error handling maintains a secure environment

### Getting Further Help

If you encounter issues not covered in this guide or need additional assistance:

1. Check the API documentation at `/docs` endpoint
2. Review the troubleshooting section for common issues
3. Examine logs for error details
4. Contact system administrators for account-specific issues

### Future Development

The RAG System is continuously evolving with planned enhancements:

- Support for additional embedding models
- Enhanced filtering capabilities for search results
- Integration with document processing pipelines
- Advanced analytics on search patterns and document usage
- Multi-language support for international content

---

Thank you for using the RAG System. We hope this guide helps you effectively leverage the power of vector search and semantic document retrieval in your applications.

*Last updated: April 2025*
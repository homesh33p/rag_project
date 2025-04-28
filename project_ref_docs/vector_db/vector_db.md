### [_Index_](../index.md)

### [How do vector databases operate](./vector_db_overview.md) (focus on PGVector)

### [How to design a database model for a vector store](./dbmodel_for_csv.md)

To store CSV content into the pgvector database, follow these steps:

1. Prepare your CSV file:
- Ensure it contains the content you want to vectorize in a specific column
- Example format similar to "userguide.csv" with content in a column like
"enhancedContent"

```py
# 2. Set up embedding model:
from langchain_community.embeddings import HuggingFaceEmbeddings

# Choose an appropriate model for your content
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")

# 3. Configure database connection:
CONNECTION_STRING = "postgresql+psycopg2://username:password@host/database?sslmode=require"

# 4. Load and store the data:
from langchain_community.vectorstores import PGVector
from langchain.vectorstores.utils import DistanceStrategy
from langchain_community.document_loaders import DataFrameLoader
import pandas as pd

def create_table(filename, page_content_column, embeddings, collection_name):
    # Read CSV into DataFrame
    df = pd.read_csv(filename)

    # Load content from specific column
    loader = DataFrameLoader(df, page_content_column=page_content_column)
    docs = loader.load()

    # Store in pgvector
    db = PGVector.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        distance_strategy=DistanceStrategy.COSINE,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True  # Set to False to append instead
    )
    return db

### Call the function with your CSV and parameters
create_table("your_data.csv", "content_column", embeddings, "your_collection")
```

These steps will read your CSV, generate embeddings for the specified content column, and
store them in the pgvector database.
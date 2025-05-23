### [_Index_](../index.md)

### _Next_

```txt
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Question-Answering Agent                 │
└───────────────┬─────────────────────────────────▲───────────────┘
                │                                 │
┌───────────────▼───────────────┐  ┌─────────────────────────────┐
│       Query Understanding     │  │      Response Generation    │
│                               │  │                             │
│ - Query preprocessing         │  │ - Context merging           │
│ - Query classification        │  │ - Response formatting       │
│ - Query expansion             │  │ - Citation generation       │
└───────────────┬───────────────┘  └──────────────▲──────────────┘
                │                                 │
┌───────────────▼───────────────┐  ┌──────────────┴──────────────┐
│      Retrieval Pipeline       │  │      LLM Integration        │
│                               │  │                             │
│ - Hybrid retrieval            │  │ - Prompt engineering        │
│   - TF-IDF retrieval          │  │ - Few-shot examples         │
│   - Vector search             │  │ - Response templates        │
│ - Result re-ranking           │  │ - Chain-of-thought          │
└───────────────┬───────────────┘  └──────────────▲──────────────┘
                │                                 │
                └─────────────────┬───────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                        Storage Layer                            │
│                                                                 │
│ - pgvector for vector embeddings                                │
│ - TF-IDF model for keyword matching                             │
│ - Document metadata                                             │
└─────────────────────────────────────────────────────────────────┘
```

### [Query preprocessing](./query_preprocessing.md)
Query preprocessing improves the quality of search results by cleaning and normalizing the query text before vector embedding or TF-IDF processing.

### Query classification
Query classification helps determine the most appropriate search method for different query types.
```py
# Keywords that suggest factual or lookup queries (better for TF-IDF)
self.factual_keywords = [
    'what is', 'how to', 'define', 'explain', 'steps', 'procedure', 
    'meaning', 'definition', 'example', 'installation', 'setup'
]

# Keywords that suggest semantic or conceptual queries (better for vector search)
self.semantic_keywords = [
    'similar to', 'related', 'like', 'compare', 'difference', 
    'alternative', 'best practice', 'recommend', 'suggest'
]
```

### [Query expansion](./query_expansion.md)
Query expansion enriches the original query with related terms to improve recall.

The query preprocessing cleans and normalizes input, query classification selects the optimal search method, and query expansion improves recall by incorporating related terms.

### Few-shot examples
This technique enables in-context learning where the model uses provided examples to guide its responses.
Few-shot prompting works by providing "demonstrations in the prompt to steer the model to better performance" where these demonstrations serve as conditioning for subsequent examples.
ex: 
```txt
USER QUERY: What does pgvector do?

FEW-SHOT EXAMPLES:
Query: What are vector embeddings?
Response: Vector embeddings are numerical representations of data (like text or images) that capture semantic meaning in a multi-dimensional space. In our RAG system, documents are converted to 768-dimensional vectors using the all-mpnet-base-v2 model, allowing for similarity-based search.

Query: How do I create a document?
Response: You can create a document via our API by sending a POST request to /api/v1/documents with a JSON body containing "title" and "content" fields. The document will automatically be embedded and stored in the pgvector database.
```

### Response templates
Templates for documents can be offered "to ensure the AI's response follows a desired structure and format.
ex:
```txt
When answering user questions about our documentation, always use this format:

ANSWER: [Provide a direct, concise answer to the question]

DETAILS: [Provide additional context and explanation]

RELATED SECTIONS: [List 1-3 related sections from the documentation with links]

EXAMPLE CODE: [If applicable, provide a code example]
```

### Chain-of-thought
Chain-of-Thought (CoT) prompting is a technique that enhances AI reasoning by encouraging the model to break down complex problems into intermediate steps before providing a final answer.
In standard prompt formats, models typically provide direct responses, but CoT "simulates human-like reasoning processes by breaking down elaborate problems into manageable, intermediate steps that sequentially lead to a conclusive answer.

```txt
USER QUERY: I have a CSV with user data and want to store it in the pgvector database. How should I process this?

SYSTEM PROMPT (with CoT instruction):
Think through this request step by step. First, understand what the user needs to do with their CSV data. Then, explain how the data should be prepared for vector embedding. Next, describe the process for storing these embeddings in pgvector. Finally, provide information about how they can query this data once it's stored.
```

With this CoT approach, the model's response will methodically walk through each stage of the process:

Understanding the user's CSV structure
Preparing the data (cleaning, normalization)
Generating embeddings using the appropriate model
Storing these embeddings in the pgvector database
Explaining how to query the data effectively

This structured reasoning helps users understand not just what to do but why each step matters, resulting in more comprehensive and helpful responses.

### [_Index_](../index.md)

### _Next_

### [_back_](./index.md#query-expansion)

# Query Expansion in RAG Systems

Query expansion is a powerful technique that enriches a user's original query with additional related terms to improve search recall. Let me explain in detail how the `QueryExpander` class in the example works and what benefits it provides to your RAG system with pgvector.

## What Query Expansion Accomplishes

At its core, query expansion addresses a fundamental challenge in information retrieval: the vocabulary mismatch problem. Users often use different terminology than what appears in the documents, even when referring to the same concepts. Query expansion bridges this gap.

## How the QueryExpander Implementation Works

Let's break down the `QueryExpander` class from the example:

### 1. Domain-Specific Term Expansions

```python
self.term_expansions = {
    "api": ["endpoint", "rest", "request", "response", "http"],
    "authentication": ["auth", "login", "credentials", "token", "api key"],
    "database": ["pgvector", "postgresql", "sql", "vector", "index"],
    "embedding": ["vector", "encoding", "representation", "similarity"],
    "setup": ["installation", "configuration", "initialize", "configure"],
    "document": ["content", "text", "file", "csv", "pdf"]
}
```

**Purpose**:
- Provides a curated mapping of domain-specific terms to related concepts
- Addresses domain-specific vocabulary matches that general language models might miss
- Customized specifically for your RAG system's focus on vector databases and document storage

For example, when a user queries about "api", the system knows to also look for content containing "endpoint", "rest", "request", etc.

### 2. Synonym-Based Expansion

```python
def expand_with_synonyms(self, query, max_expansions=2):
    query_terms = query.lower().split()
    expansions = []
    
    for term in query_terms:
        if term in self.term_expansions:
            # Add up to max_expansions related terms
            expansions.extend(self.term_expansions[term][:max_expansions])
```

**Purpose**:
- Identifies terms in the query that have known expansions
- Controls expansion with the `max_expansions` parameter to prevent query dilution
- Creates controlled vocabulary enrichment based on domain knowledge

**Example**:  
For the query "api authentication setup", it might add expansions:
- For "api": ["endpoint", "rest"]
- For "authentication": ["token", "credentials"] 
- For "setup": ["installation", "configuration"]

### 3. Expanded Query Creation

```python
# Return original query if no expansions found
if not expansions:
    return [query]

# Create expanded query versions
expanded_queries = [query]  # Always keep the original query

# Add original query + expansions
expanded_query = f"{query} {' '.join(expansions)}"
expanded_queries.append(expanded_query)

return expanded_queries
```

**Purpose**:
- Always preserves the original query to avoid losing precision
- Creates an expanded version that includes the original terms plus related terms
- Returns a list of queries (original and expanded) for multi-query retrieval

**Example**:  
Original: "api authentication setup"  
Expanded: "api authentication setup endpoint rest token credentials installation configuration"

### 4. Multi-Query Search and Result Combination

```python
async def expand_and_search(self, query, vector_store, k=3):
    expanded_queries = self.expand_with_synonyms(query)
    all_results = []
    seen_docs = set()
    
    # Search with each expanded query
    for expanded_query in expanded_queries:
        results = await vector_store.asimilarity_search_with_score(expanded_query, k=k)
        
        for doc, score in results:
            # Use document content as the key for deduplication
            doc_key = doc.page_content
            
            if doc_key not in seen_docs:
                seen_docs.add(doc_key)
                all_results.append((doc, score))
    
    # Sort by score and limit to top k
    all_results.sort(key=lambda x: x[1], reverse=True)
    return all_results[:k]
```

**Purpose**:
- Executes searches with both the original and expanded queries
- Deduplicates results to avoid showing the same document multiple times
- Sorts by similarity score to present the most relevant results first
- Limits results to the top k to maintain result quality

## Benefits for Your RAG System

Query expansion provides several significant benefits for your pgvector-based RAG system:

### 1. Improved Recall

The primary benefit is retrieving relevant documents that wouldn't match the original query terms. For example, if a user asks about "setup", the system will also find content about "installation" and "configuration", even if those exact terms weren't in the query.

### 2. Addressing Terminology Gaps

Your userguide documentation might use technical terms like "pgvector" while users might ask about "vector database". Expansion bridges this terminology gap.

### 3. Handling Acronyms and Variants

Domain-specific terms often have acronyms or variants. Expansion helps match "auth" with "authentication", "API" with "Application Programming Interface", etc.

### 4. Balancing Precision and Recall

By keeping the original query and adding an expanded version, the system maintains high precision while improving recall. Results matching the original query terms will generally score higher, but additional relevant results are still included.

### 5. Enhanced Vector Search

For your pgvector implementation specifically, query expansion helps enrich the semantic representation. When the expanded query gets embedded using your all-mpnet-base-v2 model, the resulting vector better represents the full concept the user is asking about.

## Advanced Refinements

The example implementation could be further enhanced with:

### 1. Dynamic Expansion

Instead of a static dictionary, you could use word embeddings to dynamically find related terms:

```python
def dynamic_expansion(self, term):
    # Embed the term
    term_embedding = self.model.encode(term)
    
    # Compare with a vocabulary of domain terms
    similarities = util.cos_sim(term_embedding, self.vocabulary_embeddings)
    
    # Get top similar terms
    top_indices = torch.topk(similarities[0], k=5).indices
    expanded_terms = [self.vocabulary[idx] for idx in top_indices]
    
    return expanded_terms
```

### 2. Weighted Expansion

You could weight the original and expanded terms differently:

```python
def weighted_expansion(self, query):
    original_terms = query.split()
    expanded_terms = []
    
    for term in original_terms:
        if term in self.term_expansions:
            expanded_terms.extend(self.term_expansions[term][:2])
    
    # Create weighted query with original terms emphasized
    weighted_query = query + " " + query + " " + " ".join(expanded_terms)
    
    return weighted_query
```

### 3. Pseudo-Relevance Feedback

A more advanced technique would use the top results from an initial query to extract terms for expansion:

```python
async def pseudo_relevance_feedback(self, query, vector_store, k=3):
    # Initial search
    initial_results = await vector_store.asimilarity_search(query, k=3)
    
    # Extract key terms from top results
    expansion_terms = []
    for doc in initial_results:
        # Extract important terms from the document
        # (This is simplified - you would use TF-IDF or another method)
        content_words = [w for w in doc.page_content.split() if len(w) > 4]
        expansion_terms.extend(content_words[:5])
    
    # Create expanded query
    expanded_query = f"{query} {' '.join(set(expansion_terms))}"
    
    # Final search with expanded query
    final_results = await vector_store.asimilarity_search(expanded_query, k=k)
    
    return final_results
```

In summary, query expansion significantly enhances the RAG system's ability to retrieve relevant documentation by bridging vocabulary gaps between user queries and your stored content. It can dramatically improve the user experience by ensuring they find the information they need even when they don't use the exact terminology present in the documentation.

### [_back_](./index.md#query-expansion)
from sentence_transformers import SentenceTransformer, util
from langchain_postgres import PGVectorStore
import torch
import asyncio

class QueryExpander:
    def __init__(self, model_name="all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
        
        # Dictionary of domain-specific term expansions
        # This can be extended with domain-specific terminology
        self.term_expansions = {
            "api": ["endpoint", "rest", "request", "response", "http"],
            "authentication": ["auth", "login", "credentials", "token", "api key"],
            "database": ["pgvector", "postgresql", "sql", "vector", "index"],
            "embedding": ["vector", "encoding", "representation", "similarity"],
            "setup": ["installation", "configuration", "initialize", "configure"],
            "document": ["content", "text", "file", "csv", "pdf"]
        }
        
    def expand_with_synonyms(self, query, max_expansions=2):
        """Expand query with domain-specific synonyms"""
        query_terms = query.lower().split()
        expansions = []
        
        for term in query_terms:
            if term in self.term_expansions:
                # Add up to max_expansions related terms
                expansions.extend(self.term_expansions[term][:max_expansions])
        
        # Return original query if no expansions found
        if not expansions:
            return [query]
        
        # Create expanded query versions
        expanded_queries = [query]  # Always keep the original query
        
        # Add original query + expansions
        expanded_query = f"{query} {' '.join(expansions)}"
        expanded_queries.append(expanded_query)
        
        return expanded_queries
        
    async def expand_and_search(self, query: str, vector_store: PGVectorStore, k=3):
        """Expand query and combine search results"""
        expanded_queries = self.expand_with_synonyms(query)
        all_results = []
        seen_docs = set()
        
        # Create tasks for all queries to execute concurrently
        search_tasks = [vector_store.asimilarity_search_with_score(expanded_query, k=k) 
                        for expanded_query in expanded_queries]
        
        # Execute all search tasks concurrently
        results_list = await asyncio.gather(*search_tasks)
        
        # Process all results
        for results in results_list:
            for doc, score in results:
                # Use document content as the key for deduplication
                doc_key = doc.page_content
                
                if doc_key not in seen_docs:
                    seen_docs.add(doc_key)
                    all_results.append((doc, score))
        
        # Sort by score and limit to top k
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:k]
from fastapi import APIRouter
import asyncio

from app.utils.query_preprocessor import QueryPreprocessor
from app.utils.query_classification import QueryClassifier
from app.utils.query_expander import QueryExpander
from app.documents import SimplifiedUserGuideProcessor
from app.documents.tfidf_processor import PersistentTFIDFProcessor
from itertools import chain

router = APIRouter(tags=["query"])

@router.post("userguide/query")
async def enhanced_search(query: str, k: int = 5):
    """
    Complete search pipeline with preprocessing, classification, and expansion.
    """
    preprocessor = QueryPreprocessor()
    classifier = QueryClassifier()
    # Preprocess
    preprocessed_query = preprocessor.preprocess(query)
    
    # Classify
    query_type = classifier.classify(preprocessed_query)
        
    # Search based on query type
    if query_type == "factual":
        results = await query_with_tfidf(query,k)
    elif query_type == "semantic":
        results = await query_userguide_cosine_sim(query,k)
        for res in results:
            res.pop('score')
    else:
        results = await hybrid_search(query,k)
    return results

@router.post("userguide/query/cosinesimilarity")
async def query_userguide_cosine_sim(query: str, k: int = 3):
    """Query the userguide vector store."""
    preprocessor = QueryPreprocessor()
    # Preprocess the query
    preprocessed_query = preprocessor.preprocess(query)

    expander = QueryExpander()
    
    # Expand query and search
    expanded_queries = expander.expand_with_synonyms(query=preprocessed_query)
    all_results = []
    seen_docs = set()
    
    # Use vector search for semantic queries
    processor = SimplifiedUserGuideProcessor.get_instance()
    
    # Create search tasks for all expanded queries
    search_tasks = [
        processor.vectorstore.asimilarity_search_with_score(expanded_query, k=k)
        for expanded_query in expanded_queries
    ]
    
    # Execute all search tasks concurrently
    results_list = await asyncio.gather(*search_tasks)
    
    # Process all results
    for results in results_list:
        for doc, score in results:
            # Use document content as the key for deduplication
            doc_key = doc.page_content
            
            if doc_key not in seen_docs:
                seen_docs.add(doc_key)
                all_results.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score
                    }
                )
    
    # Sort by score and limit to top k
    all_results.sort(key=lambda x: x['score'], reverse=True)
    return all_results[:k]


@router.post("userguide/query/tfidf")
async def query_with_tfidf(query: str, k: int = 3):
    """Query the userguide using TF-IDF retrieval"""
    # For factual queries, TF-IDF works well
    tfidf_processor = PersistentTFIDFProcessor.get_instance()
    preprocessor = QueryPreprocessor()
    # Preprocess the query
    preprocessed_query = preprocessor.preprocess(query)    
    results = tfidf_processor.search(preprocessed_query, k=k)
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in results
    ]



@router.post("userguide/query/hybrid")
async def hybrid_search(query: str, k: int = 5):
    """Perform both TF-IDF and vector search, combining results"""
    # For hybrid queries, combine methods
    # TF-IDF results

    preprocessor = QueryPreprocessor()
    # Preprocess
    preprocessed_query = preprocessor.preprocess(query)
    
    tfidf_results = await query_with_tfidf(query=preprocessed_query,k=k)
    for res in tfidf_results:
        res["source"]="tfidf"
    vector_results = await query_userguide_cosine_sim(query=preprocessed_query,k=k)
    for res in vector_results:
        res["source"]="vector"    
    
    # Combine and deduplicate
    all_results = []
    seen_content = set()
    
    # Process TF-IDF results
    for res in list(chain(tfidf_results,vector_results)):
        if res["content"] not in seen_content:
            seen_content.add(res["content"])
            all_results.append(res)
    
    return all_results[:k]

from fastapi import APIRouter

from app.documents import SimplifiedUserGuideProcessor
from app.documents.tfidf_processor import PersistentTFIDFProcessor

router = APIRouter(tags=["query"])

@router.post("userguide/query")
async def query_userguide(query: str, k: int = 3):
    """Query the userguide vector store."""
    
    processor = SimplifiedUserGuideProcessor.get_instance()
    
    # Search
    results = await processor.vectorstore.asimilarity_search_with_score(query, k=k)
    
    # Return results
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": score
        }
        for doc,score in results
    ]

@router.post("userguide/query/tfidf")
async def query_with_tfidf(query: str, k: int = 3):
    """Query the userguide using TF-IDF retrieval - fast version."""
    # Get singleton instance (already initialized)
    processor = PersistentTFIDFProcessor.get_instance()
    
    # Search - no need to rebuild the model
    results = processor.search(query, k=k)
    
    # Return results
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in results
    ]

@router.post("userguide/hybrid")
async def hybrid_search(query: str, k: int = 5):
    """Perform both TF-IDF and vector search, combining results - fast version."""
    # Get TF-IDF results - using singleton instance
    tfidf_processor = PersistentTFIDFProcessor.get_instance()
    tfidf_results = tfidf_processor.search(query, k=k)
    
    # Get vector search results - already initialized
    vector_processor = SimplifiedUserGuideProcessor.get_instance()
    vector_results = await vector_processor.vectorstore.asimilarity_search(query, k=k)
    
    # Combine and deduplicate results
    all_results = []
    seen_content = set()
    
    # Process both result sets
    for doc_list in [tfidf_results, vector_results]:
        for doc in doc_list:
            # Use content as deduplication key
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                all_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
    
    return all_results[:k]

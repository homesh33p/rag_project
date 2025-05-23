class QueryClassifier:
    def __init__(self):
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
        
    def classify(self, query):
        query_lower = query.lower()
        
        # Check for factual keywords
        factual_score = sum(1 for keyword in self.factual_keywords if keyword in query_lower)
        
        # Check for semantic keywords
        semantic_score = sum(1 for keyword in self.semantic_keywords if keyword in query_lower)
        
        # Classify based on scores
        if factual_score > semantic_score:
            return "factual"
        elif semantic_score > factual_score:
            return "semantic"
        else:
            return "hybrid"  # Default to hybrid approach
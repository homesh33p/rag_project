import re
from typing import List

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class QueryPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess(self, query):
        # Convert to lowercase
        query = query.lower()
        
        # Remove special characters
        query = re.sub(r'[^\w\s]', ' ', query)
        
        # Tokenize
        tokens = word_tokenize(query)
        
        # Remove stopwords and lemmatize
        preprocessed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words
        ]
        
        # Reconstruct the query
        preprocessed_query = ' '.join(preprocessed_tokens)
        
        return preprocessed_query

class QueryPreProcessor:
    """Process and optimize queries for retrieval"""
    
    def __init__(self):
        # Common terms to remove for better vector search
        self.filter_terms = ['how', 'what', 'when', 'why', 'can', 'does', 'is', 'are']
        self.query_templates = [
            "{}",  # Original query
            "How to {}?",  # How-to variant
            "What is {}?"   # Definition variant
        ]
    
    def process(self, query: str) -> str:
        """Process the query for optimal retrieval"""
        # Clean the query
        query = query.strip()
        
        # Remove trailing punctuation
        query = re.sub(r'[?!.,;:]+$', '', query)
        
        return query
    
    def expand_query(self, query: str) -> List[str]:
        """Generate query variations to improve retrieval chances"""
        # Basic query without question words for vector search
        base_query = ' '.join([
            word for word in query.lower().split() 
            if word not in self.filter_terms
        ])
        
        # Generate variations
        variations = [template.format(base_query) for template in self.query_templates]
        
        # Add original query
        if query not in variations:
            variations.append(query)
            
        return variations
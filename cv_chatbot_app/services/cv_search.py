from .qdrant_service import search_points
from .embedding import generate_embedding

def search_cv(collection_name, query, limit=10):
    """Searches for relevant chunks in a CV based on the query"""
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        
        # Search in Qdrant
        search_results = search_points(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return search_results
    except Exception as e:
        print(f"Error searching CV: {str(e)}")
        return []
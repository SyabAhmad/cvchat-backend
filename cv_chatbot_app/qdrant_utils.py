import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from sentence_transformers import SentenceTransformer
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Qdrant client
QDRANT_API_KEY = os.getenv('Qdrant_API_KEY')
QDRANT_URL = os.getenv('Qdrant_client_url')

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

def create_collection_for_cv(cv_name):
    """Creates a new collection in Qdrant for a CV"""
    collection_name = f"cv_{uuid.uuid4().hex}"
    
    # Create collection with proper vector configuration
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=qdrant_models.VectorParams(
            size=384,  # Matches the embedding model's output dimension
            distance=qdrant_models.Distance.COSINE
        )
    )
    
    return collection_name

def store_cv_chunk(collection_name, chunk_text, chunk_index):
    """Stores a CV chunk in Qdrant"""
    try:
        print(f"Generating embedding for chunk {chunk_index}")
        # Generate embedding for the chunk
        embedding = embedding_model.encode(chunk_text)
        
        # Create a valid point ID
        point_id = str(uuid.uuid4())
        
        print(f"Storing chunk {chunk_index} in Qdrant")
        # Store in Qdrant
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "text": chunk_text,
                        "chunk_index": chunk_index
                    }
                )
            ]
        )
        print(f"Successfully stored chunk {chunk_index}")
        return point_id
    except Exception as e:
        print(f"Error storing chunk {chunk_index}: {str(e)}")
        # Return a placeholder ID so the process doesn't break
        # In production, you'd want better error handling
        return f"error_{chunk_index}"

def search_cv(collection_name, query, limit=5):
    """Searches a CV collection for relevant chunks based on a query"""
    try:
        # Generate embedding for the query
        query_embedding = embedding_model.encode(query)
        
        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding.tolist(),
            limit=limit
        )
        
        return search_results
    except Exception as e:
        print(f"Error searching CV: {str(e)}")
        return []

def delete_collection(collection_name):
    """Deletes a collection from Qdrant"""
    qdrant_client.delete_collection(collection_name=collection_name)
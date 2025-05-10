import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Qdrant client
QDRANT_API_KEY = os.getenv('Qdrant_API_KEY')
QDRANT_URL = os.getenv('Qdrant_client_url')

def get_qdrant_client():
    """Returns a configured Qdrant client"""
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )

def create_collection(collection_name, vector_size=384):
    """Creates a new collection in Qdrant"""
    client = get_qdrant_client()
    client.create_collection(
        collection_name=collection_name,
        vectors_config=qdrant_models.VectorParams(
            size=vector_size,
            distance=qdrant_models.Distance.COSINE
        )
    )
    
def delete_collection(collection_name):
    """Deletes a collection from Qdrant"""
    client = get_qdrant_client()
    client.delete_collection(collection_name=collection_name)

def upsert_points(collection_name, points):
    """Upserts points into a Qdrant collection"""
    client = get_qdrant_client()
    client.upsert(
        collection_name=collection_name,
        points=points
    )

def search_points(collection_name, query_vector, limit=5):
    """Searches for points in a Qdrant collection"""
    client = get_qdrant_client()
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit
    )

def generate_collection_name():
    """Generates a unique collection name"""
    return f"cv_{uuid.uuid4().hex}"
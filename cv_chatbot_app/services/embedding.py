from sentence_transformers import SentenceTransformer

# Initialize the embedding model (singleton pattern)
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
    return _embedding_model

def generate_embedding(text):
    model = get_embedding_model()
    return model.encode(text).tolist()
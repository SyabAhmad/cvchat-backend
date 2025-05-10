import os
import PyPDF2
import docx
import uuid
from qdrant_client.http import models as qdrant_models
from ..models import CV, CVChunk
from .qdrant_service import get_qdrant_client, generate_collection_name, create_collection
from .embedding import generate_embedding
import re

def extract_text_from_file(file_obj):
    """Extracts text from a file based on its extension"""
    text = ""
    file_extension = os.path.splitext(file_obj.name)[1].lower()
    
    if file_extension == '.pdf':
        pdf_reader = PyPDF2.PdfReader(file_obj)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    elif file_extension in ['.doc', '.docx']:
        doc = docx.Document(file_obj)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
        
    return text

def create_chunks(text, chunk_size=500, overlap=1):
    """
    Create overlapping chunks of full sentences from the text.
    Preprocessing includes normalization, extra space removal, and dash handling.
    """
    # Normalize and clean text
    text = text.replace('\n', ' ').replace('\r', '')
    text = re.sub(r'\s*[-–—]+\s*', ' ', text)
    text = ' '.join(text.split())

    # Split text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if current_length + len(sentence) <= chunk_size:
            current_chunk.append(sentence)
            current_length += len(sentence)
        else:
            # Commit current chunk
            if current_chunk:
                chunks.append(' '.join(current_chunk))

                # Handle overlap (by sentence count)
                current_chunk = current_chunk[-overlap:] if overlap > 0 else []
                current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += len(sentence)

    # Add any leftover
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def store_cv_chunks(name, collection_name, chunks_with_embeddings):
    """
    Store preprocessed CV chunks and their embeddings into Qdrant and the database.

    Parameters:
    - name: Name of the CV owner.
    - collection_name: The name of the pre-created Qdrant collection.
    - chunks_with_embeddings: A list of tuples (chunk_text, embedding).
    """
    try:
        # Create CV record in database
        cv = CV.objects.create(
            name=name,
            qdrant_collection_name=collection_name
        )

        points = []
        chunk_records = []

        for i, (chunk_text, embedding) in enumerate(chunks_with_embeddings):
            if len(chunk_text.strip()) < 20:
                continue

            point_id = str(uuid.uuid4())

            # Prepare point for Qdrant
            points.append(
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={"text": chunk_text, "chunk_index": i}
                )
            )

            # Prepare DB chunk record
            chunk_records.append(
                CVChunk(
                    cv=cv,
                    chunk_index=i,
                    chunk_text=chunk_text,
                    qdrant_point_id=point_id
                )
            )

        # Store in Qdrant
        if points:
            client = get_qdrant_client()
            client.upsert(
                collection_name=collection_name,
                points=points
            )

        # Store in DB
        if chunk_records:
            CVChunk.objects.bulk_create(chunk_records)

        return cv

    except Exception as e:
        print(f"Error storing CV: {str(e)}")
        raise

def process_and_store_cv(name, file_obj):
    """Process and store a CV file with its embeddings"""
    try:
        # Extract text from the file
        text = extract_text_from_file(file_obj)
        
        # Create a collection in Qdrant
        collection_name = generate_collection_name()
        create_collection(collection_name)
        
        # Create chunks
        chunks = create_chunks(text)
        
        # Generate embeddings for each chunk
        chunks_with_embeddings = []
        for chunk_text in chunks:
            if len(chunk_text.strip()) < 20:  # Skip very small chunks
                continue
            embedding = generate_embedding(chunk_text)
            chunks_with_embeddings.append((chunk_text, embedding))
        
        # Store the CV and chunks
        cv = store_cv_chunks(name, collection_name, chunks_with_embeddings)
        
        return cv
        
    except Exception as e:
        print(f"Error processing CV: {str(e)}")
        raise

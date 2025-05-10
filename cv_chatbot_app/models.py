from django.db import models
from pgvector.django import VectorField

class CV(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255) 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Store the Qdrant collection name/ID associated with this CV
    qdrant_collection_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"CV {self.id} - {self.name}"

class CVChunk(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    chunk_text = models.TextField()
    # Store the Qdrant point ID for this chunk
    qdrant_point_id = models.CharField(max_length=255)
    

    def __str__(self):
        return f"Chunk {self.chunk_index} of CV {self.cv.name}"

class Conversation(models.Model):
    question = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    related_cv = models.ForeignKey(CV, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Conversation at {self.timestamp}"

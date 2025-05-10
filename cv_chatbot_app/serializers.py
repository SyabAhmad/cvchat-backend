from rest_framework import serializers
from .models import CV, CVChunk, Conversation

class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['id', 'name', 'uploaded_at', 'qdrant_collection_name']

class CVChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVChunk
        fields = ['id', 'cv', 'chunk_index', 'chunk_text', 'qdrant_point_id']

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'question', 'response', 'timestamp', 'related_cv']
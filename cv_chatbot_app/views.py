import os
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from .models import CV, Conversation
from .serializers import CVSerializer, ConversationSerializer
from .services.cv_upload import store_cv_chunks, process_and_store_cv
from .services.cv_search import search_cv
from .services.ai_service import generate_response
from .services.qdrant_service import delete_collection
import uuid
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client for generating responses
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
groq_client = groq.Client(api_key=GROQ_API_KEY)

class CVViewSet(viewsets.ModelViewSet):
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_cv(self, request):
        file_obj = request.FILES.get('file')
        name = request.data.get('name')
        
        if not file_obj or not name:
            return Response({"error": "Both file and name are required"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Add detailed logging
            print(f"Starting CV upload process for {name}")
            # This should call your process_and_store_cv function
            cv = process_and_store_cv(name, file_obj)
            print(f"Successfully processed CV: {cv.id}")
            return Response(CVSerializer(cv).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            print(f"ValueError in CV upload: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(f"Error processing CV: {str(e)}")
            print(traceback.format_exc())  # This will print the full stack trace
            return Response({"error": f"Error processing CV: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        cv = self.get_object()
        # Delete the collection from Qdrant
        delete_collection(cv.qdrant_collection_name)
        # Then proceed with the default delete behavior
        return super().destroy(request, *args, **kwargs)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

@api_view(['POST'])
def chat_with_cv(request):
    cv_id = request.data.get('cv_id')
    question = request.data.get('question')
    
    if not cv_id or not question:
        return JsonResponse({"error": "Both cv_id and question are required"}, status=400)
    
    try:
        cv = CV.objects.get(id=cv_id)
    except CV.DoesNotExist:
        return JsonResponse({"error": "CV not found"}, status=404)
    
    # Search for relevant chunks in Qdrant
    search_results = search_cv(cv.qdrant_collection_name, question, limit=3)
    
    # Prepare context from search results
    context = "\n\n".join([result.payload["text"] for result in search_results])
    
    # Generate response using AI service
    response_text = generate_response(context, question)
    
    # Save the conversation
    conversation = Conversation.objects.create(
        question=question,
        response=response_text,
        related_cv=cv
    )
    
    return JsonResponse({
        "response": response_text
    })

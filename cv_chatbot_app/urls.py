from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cvs', views.CVViewSet)
router.register(r'conversations', views.ConversationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', views.chat_with_cv, name='chat_with_cv'),
    path('cvs/upload_cv/', views.CVViewSet.as_view({'post': 'upload_cv'}), name='upload_cv'),
]
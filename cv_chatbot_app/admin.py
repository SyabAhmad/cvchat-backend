from django.contrib import admin
from .models import CV, CVChunk, Conversation
# Register your models here.

admin.site.register(CV)
admin.site.register(CVChunk)
admin.site.register(Conversation)

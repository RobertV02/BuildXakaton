from django.contrib import admin
from .models import Attachment

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'content_type', 'size', 'uploaded_by', 'created_at', 'updated_at')
    list_filter = ('content_type', 'uploaded_by', 'created_at', 'updated_at')
    search_fields = ('name', 'file', 'content_type')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

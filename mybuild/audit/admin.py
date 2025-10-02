from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'model', 'object_id', 'was_offline', 'created_at']
    list_filter = ['action', 'model', 'was_offline', 'created_at']
    search_fields = ['actor__username', 'action', 'model', 'object_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'client_created_at']
    ordering = ['-created_at']

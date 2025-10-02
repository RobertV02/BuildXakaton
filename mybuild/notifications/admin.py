from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'kind', 'is_read', 'created_at']
    list_filter = ['kind', 'is_read', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'kind']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

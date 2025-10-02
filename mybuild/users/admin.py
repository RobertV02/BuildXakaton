from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'position', 'organization', 'created_at']
    list_filter = ['organization', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone', 'position']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['user__username']

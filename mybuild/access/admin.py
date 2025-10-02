from django.contrib import admin
from .models import Invitation

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'org', 'role', 'object', 'invited_by', 'status', 'expires_at', 'created_at')
    list_filter = ('status', 'role', 'org', 'object', 'invited_by', 'expires_at', 'created_at')
    search_fields = ('email', 'org__name', 'invited_by__username')
    readonly_fields = ('id', 'token', 'created_at', 'updated_at')
    ordering = ('-created_at',)

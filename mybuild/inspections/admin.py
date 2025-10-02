from django.contrib import admin
from .models import PresenceToken, InspectionVisit, PresenceConfirmation


@admin.register(PresenceToken)
class PresenceTokenAdmin(admin.ModelAdmin):
    list_display = ['object', 'method', 'is_revoked', 'expires_at', 'created_by', 'created_at']
    list_filter = ['method', 'is_revoked', 'expires_at', 'created_at']
    search_fields = ['object__name', 'token', 'created_by__username']
    readonly_fields = ['id', 'token', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(InspectionVisit)
class InspectionVisitAdmin(admin.ModelAdmin):
    list_display = ['object', 'inspector', 'started_at', 'ended_at', 'latitude', 'longitude']
    list_filter = ['started_at', 'ended_at']
    search_fields = ['object__name', 'inspector__username', 'note']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-started_at']


@admin.register(PresenceConfirmation)
class PresenceConfirmationAdmin(admin.ModelAdmin):
    list_display = ['visit', 'status', 'method', 'confirmed_at']
    list_filter = ['status', 'method', 'confirmed_at']
    search_fields = ['visit__inspector__username', 'visit__object__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'confirmed_at']
    ordering = ['-created_at']

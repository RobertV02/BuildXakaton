from django.contrib import admin
from .models import ScheduleRevision, WorkItem, ChangeRequest


@admin.register(ScheduleRevision)
class ScheduleRevisionAdmin(admin.ModelAdmin):
    list_display = ['object', 'version', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['object__name', 'created_by__username', 'note']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'revision', 'start_planned', 'end_planned', 'progress_percent']
    list_filter = ['start_planned', 'end_planned', 'progress_percent']
    search_fields = ['name', 'revision__object__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['start_planned']


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ['object', 'proposed_by', 'status', 'reviewed_by', 'created_at']
    list_filter = ['status', 'created_at', 'reviewed_at']
    search_fields = ['object__name', 'proposed_by__username', 'reviewed_by__username', 'comment']
    readonly_fields = ['id', 'created_at', 'updated_at', 'reviewed_at']
    ordering = ['-created_at']

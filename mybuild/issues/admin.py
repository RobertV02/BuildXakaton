from django.contrib import admin
from .models import IssueCategory, Remark, Violation, Resolution


@admin.register(IssueCategory)
class IssueCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'issuer_type', 'created_at']
    list_filter = ['issuer_type', 'created_at']
    search_fields = ['title', 'code']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['title']


@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ['name', 'object', 'status', 'severity', 'created_by', 'created_at']
    list_filter = ['status', 'severity', 'fixability', 'issue_type', 'created_at']
    search_fields = ['name', 'description', 'object__name', 'created_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ['object', 'status', 'severity', 'created_by', 'created_at']
    list_filter = ['status', 'severity', 'created_at']
    search_fields = ['description', 'object__name', 'created_by__username', 'normative_link']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Resolution)
class ResolutionAdmin(admin.ModelAdmin):
    list_display = ['remark', 'violation', 'created_by', 'is_accepted', 'accepted_by', 'created_at']
    list_filter = ['is_accepted', 'created_at', 'accepted_at']
    search_fields = ['text', 'created_by__username', 'accepted_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'accepted_at']
    ordering = ['-created_at']

from django.contrib import admin
from .models import ConstructionObject, ObjectAssignment, OpeningChecklist, OpeningAct


@admin.register(ConstructionObject)
class ConstructionObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'org', 'status', 'created_at', 'activated_at']
    list_filter = ['status', 'org', 'created_at', 'activated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'activated_at', 'activated_by']
    ordering = ['-created_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'org')
        }),
        ('Статус и сроки', {
            'fields': ('status', 'plan_start', 'plan_end', 'activated_at', 'activated_by')
        }),
        ('Техническая информация', {
            'fields': ('polygon',),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ObjectAssignment)
class ObjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'object', 'role', 'is_active', 'assigned_by', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'object__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(OpeningChecklist)
class OpeningChecklistAdmin(admin.ModelAdmin):
    list_display = ['object', 'filled_by', 'status', 'submitted_at', 'reviewed_by', 'created_at']
    list_filter = ['status', 'submitted_at', 'reviewed_at', 'created_at']
    search_fields = ['object__name', 'filled_by__username', 'review_comment']
    readonly_fields = ['id', 'created_at', 'updated_at', 'submitted_at', 'reviewed_at']
    ordering = ['-created_at']


@admin.register(OpeningAct)
class OpeningActAdmin(admin.ModelAdmin):
    list_display = ['object', 'uploaded_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['object__name', 'uploaded_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

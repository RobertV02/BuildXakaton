from django.contrib import admin
from .models import Organization, Membership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'org', 'role', 'created_at']
    list_filter = ['role', 'org', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'org__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

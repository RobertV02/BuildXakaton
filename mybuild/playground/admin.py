from django.contrib import admin
from .models import PhotoTest

@admin.register(PhotoTest)
class PhotoTestAdmin(admin.ModelAdmin):
    list_display = ('image', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('image',)
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)

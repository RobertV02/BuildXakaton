from django.contrib import admin
from .models import MaterialType, OCRResult, TTNDocument, QualityPassport, Delivery


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'created_at']
    search_fields = ['name', 'unit']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']


@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    list_display = ['source_file', 'success', 'created_at']
    list_filter = ['success', 'created_at']
    search_fields = ['source_file__name', 'raw_text']
    readonly_fields = ['id', 'created_at', 'updated_at', 'parsed', 'raw_text']
    ordering = ['-created_at']


@admin.register(TTNDocument)
class TTNDocumentAdmin(admin.ModelAdmin):
    list_display = ['number', 'date', 'attachment', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['number', 'attachment__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(QualityPassport)
class QualityPassportAdmin(admin.ModelAdmin):
    list_display = ['number', 'date', 'attachment', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['number', 'attachment__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['object', 'material', 'quantity', 'delivered_at', 'created_by']
    list_filter = ['delivered_at', 'material', 'object', 'created_at']
    search_fields = ['object__name', 'material__name', 'created_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-delivered_at']

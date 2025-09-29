from __future__ import annotations

from rest_framework import serializers
from .models import Delivery, TTNDocument, OCRResult, MaterialType, QualityPassport, LabSampleRequest


class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = ['id', 'name', 'unit']


class OCRResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = OCRResult
        fields = '__all__'
        read_only_fields = ['success', 'error']


class TTNDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTNDocument
        fields = '__all__'


class QualityPassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityPassport
        fields = '__all__'


class DeliveryListSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    object_name = serializers.CharField(source='object.name', read_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'object', 'object_name', 'material', 'material_name', 'quantity', 'delivered_at']


class DeliveryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'


class LabSampleRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabSampleRequest
        fields = '__all__'

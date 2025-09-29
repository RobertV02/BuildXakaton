from __future__ import annotations

from rest_framework import serializers
from .models import Remark, Violation, Resolution, IssueCategory


class IssueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueCategory
        fields = ['id', 'title', 'code', 'issuer_type']


class RemarkListSerializer(serializers.ModelSerializer):
    object_name = serializers.CharField(source='object.name', read_only=True)

    class Meta:
        model = Remark
        fields = ['id', 'object', 'object_name', 'status', 'severity', 'created_at', 'client_created_at']


class RemarkDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remark
        fields = '__all__'


class ViolationListSerializer(serializers.ModelSerializer):
    object_name = serializers.CharField(source='object.name', read_only=True)

    class Meta:
        model = Violation
        fields = ['id', 'object', 'object_name', 'status', 'severity', 'created_at', 'client_created_at']


class ViolationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Violation
        fields = '__all__'


class ResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resolution
        fields = '__all__'

from __future__ import annotations

from rest_framework import serializers
from .models import ConstructionObject, OpeningChecklist


class ConstructionObjectListSerializer(serializers.ModelSerializer):
    org_id = serializers.UUIDField(source='org.id', read_only=True)

    class Meta:
        model = ConstructionObject
        fields = [
            'id', 'name', 'org_id', 'status', 'plan_start', 'plan_end', 'activated_at'
        ]


class ConstructionObjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionObject
        fields = '__all__'
        read_only_fields = ['activated_at', 'activated_by']

    def validate(self, attrs):
        # Ограничение: polygon обязателен при создании
        if self.instance is None and not attrs.get('polygon'):
            raise serializers.ValidationError({'polygon': 'Поле обязательно.'})
        return attrs


class OpeningChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningChecklist
        fields = '__all__'
        read_only_fields = ['submitted_at', 'reviewed_at', 'reviewed_by']

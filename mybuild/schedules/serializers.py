from __future__ import annotations

from rest_framework import serializers
from .models import WorkItem, ScheduleRevision, ChangeRequest


class WorkItemListSerializer(serializers.ModelSerializer):
    revision_id = serializers.UUIDField(source='revision.id', read_only=True)

    class Meta:
        model = WorkItem
        fields = ['id', 'name', 'revision_id', 'start_planned', 'end_planned', 'progress_percent']


class WorkItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = '__all__'


class ScheduleRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleRevision
        fields = '__all__'


class ChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeRequest
        fields = '__all__'

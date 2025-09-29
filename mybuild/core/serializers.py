"""Временные сериализаторы-плейсхолдеры.

Каждый ViewSet сейчас использует DefaultSerializer до определения
предметных сериализаторов. Позже будет заменено.
"""
from __future__ import annotations

from rest_framework import serializers


class DefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = None  # type: ignore
        fields: list[str] | str = '__all__'

    def get_fields(self):  # type: ignore[override]
        # Динамически строим поля на основе мета model (уже привязанного в view)
        if self.Meta.model is None and hasattr(self, 'Meta'):
            # Попытка взять модель из view (context['view'].)
            view = self.context.get('view')
            if view is not None:
                self.Meta.model = getattr(view, 'queryset').model  # type: ignore
        return super().get_fields()

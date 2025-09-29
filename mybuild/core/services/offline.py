"""Offline idempotency utilities.

create_or_get_offline(model, defaults, offline_batch_id, user?) will return existing
row with same offline_batch_id (and optionally same creator) for models using OfflineFieldsMixin.
"""
from __future__ import annotations

from typing import Type, Tuple, Dict, Any, Optional
from django.db import transaction
from django.db.models import Model, QuerySet


def create_or_get_offline(
    model: Type[Model],
    *,
    offline_batch_id: Optional[str],
    unique_with_user: bool = True,
    user_field: str | None = 'created_by',
    user=None,
    defaults: Dict[str, Any],
) -> Tuple[Model, bool]:
    """Idempotent create for offline submissions.

    Returns (instance, created_flag).
    If offline_batch_id is empty -> normal create path (created=True).
    """
    if not offline_batch_id:
        obj = model.objects.create(**defaults)
        return obj, True

    filters = {'offline_batch_id': offline_batch_id}
    if unique_with_user and user_field and user and hasattr(model, user_field):
        filters[user_field] = user

    with transaction.atomic():
        existing = model.objects.filter(**filters).first()
        if existing:
            return existing, False
        obj = model.objects.create(**defaults)
        return obj, True


__all__ = ['create_or_get_offline']

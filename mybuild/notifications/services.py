"""Notification service utilities.

Lightweight abstraction around creating Notification records so that
business logic (viewsets, signals, FSM transitions) can fire events
without duplicating code. For now it stores rows only; later we can
extend with async fan‑out (websocket, email, push) by swapping the
backend inside notify().
"""
from __future__ import annotations

from typing import Iterable, Sequence, Mapping, Any

from django.contrib.auth.models import User
from django.db import transaction

from .models import Notification

# Canonical notification kind constants (helps avoiding typos)
OBJECT_CREATED = 'object.created'
OBJECT_UPDATED = 'object.updated'
DELIVERY_CREATED = 'delivery.created'
DELIVERY_UPDATED = 'delivery.updated'
REMARK_CREATED = 'remark.created'
REMARK_UPDATED = 'remark.updated'
VIOLATION_CREATED = 'violation.created'
VIOLATION_UPDATED = 'violation.updated'


def notify(users: Iterable[User], kind: str, payload: Mapping[str, Any] | None = None) -> int:
    """Create notification rows for each user.

    Returns number of notifications created. Silently skips if users empty.
    """
    users_list: list[User] = [u for u in users if u and u.pk]
    if not users_list:
        return 0
    payload_dict = dict(payload or {})
    to_create = [Notification(user=u, kind=kind, payload=payload_dict) for u in users_list]
    with transaction.atomic():
        created = Notification.objects.bulk_create(to_create, ignore_conflicts=True)
    return len(created)


def notify_one(user: User, kind: str, payload: Mapping[str, Any] | None = None) -> int:
    return notify([user], kind, payload)


def build_basic_payload(instance) -> dict[str, Any]:  # small helper used by viewsets
    return {
        'model': instance._meta.label_lower,
        'id': str(getattr(instance, 'pk', '')),
        'repr': str(instance),
    }


__all__ = [
    'notify', 'notify_one', 'build_basic_payload',
    'OBJECT_CREATED', 'OBJECT_UPDATED',
    'DELIVERY_CREATED', 'DELIVERY_UPDATED',
    'REMARK_CREATED', 'REMARK_UPDATED',
    'VIOLATION_CREATED', 'VIOLATION_UPDATED',
]

"""Сервис аудита действий.

log_action фиксирует изменение состояния бизнес‑объекта.
Минимальный формат diff: {'field': {'from': old, 'to': new}}.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional
import uuid


def _jsonable(value: Any) -> Any:
    """Convert value into JSON‑serializable primitive.

    - UUID -> str
    - model instance -> str(pk)
    - other unsupported types -> repr()
    """
    if isinstance(value, uuid.UUID):
        return str(value)
    from django.db import models as _m
    if isinstance(value, _m.Model):
        return str(getattr(value, 'pk', value))
    try:
        # basic types pass through
        import json as _json
        _json.dumps(value)
        return value
    except Exception:  # pragma: no cover - fallback path
        return repr(value)
from django.contrib.auth.models import User
from django.db import models

from .models import AuditLog


def build_diff(before: Optional[models.Model], after: models.Model, include: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    diff: Dict[str, Any] = {}
    if before is None:
        # создание: фиксируем initial snapshot
        for f in after._meta.fields:
            name = f.name
            if include and name not in include:
                continue
            diff[name] = {'from': None, 'to': _jsonable(getattr(after, name))}
        return diff
    assert before.__class__ is after.__class__
    for f in after._meta.fields:
        name = f.name
        if name in ('created_at', 'updated_at'):
            continue
        if include and name not in include:
            continue
        old = _jsonable(getattr(before, name))
        new = _jsonable(getattr(after, name))
        if old != new:
            diff[name] = {'from': old, 'to': new}
    return diff


def log_action(
    *,
    actor: Optional[User],
    action: str,
    instance: models.Model,
    before: Optional[models.Model] = None,
    after: Optional[models.Model] = None,
    extra: Optional[Dict[str, Any]] = None,
    client_payload: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    after = after or instance
    diff = build_diff(before, after)
    context = {
        'action': action,
        'diff': diff,
    }
    if extra:
        context['extra'] = extra
    if client_payload:
        context['client'] = client_payload
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        model=instance._meta.label_lower,
        object_id=str(getattr(instance, 'pk')),
        context=context,
        client_created_at=getattr(instance, 'client_created_at', None),
        client_lat=getattr(instance, 'client_lat', None),
        client_lon=getattr(instance, 'client_lon', None),
        offline_batch_id=getattr(instance, 'offline_batch_id', None),
        was_offline=getattr(instance, 'was_offline', False),
    )

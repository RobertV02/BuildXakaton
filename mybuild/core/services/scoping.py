"""Сервисы объектного скоупинга.

Функции здесь инкапсулируют правила видимости данных пользователю
по его членствам в организациях и назначениях на объекты.
"""
from __future__ import annotations

from typing import Iterable, Set
from django.contrib.auth.models import User
from django.db.models import QuerySet


def get_user_org_ids(user: User) -> Set[int]:
    """Возвращает множество ID организаций, где пользователь состоит (Membership).

    Анонимный пользователь получает пустое множество.
    """
    if user.is_anonymous:
        return set()
    # Импорт внутри функции чтобы избежать циклических импортов
    from orgs.models import Membership

    return set(
        Membership.objects.filter(user=user).values_list("org_id", flat=True)
    )


def get_user_object_ids(user: User) -> Set[int]:
    """Возвращает множество ID объектов строительства, где пользователь назначен."""
    if user.is_anonymous:
        return set()
    from objects.models import ObjectAssignment

    return set(
        ObjectAssignment.objects.filter(user=user, is_active=True).values_list(
            "object_id", flat=True
        )
    )


def scope_qs_to_user(qs: QuerySet, user: User) -> QuerySet:
    """Ограничивает queryset данными доступными пользователю.

    Поддерживает модели содержащие поле org (FK на Organization) или object (FK на ConstructionObject).
    Если у модели есть оба — применяется OR.
    Если ни одно поле не найдено — возвращаем qs без изменений (предполагается дополнительная проверка на уровне вью).
    """
    if user.is_superuser:
        return qs
    # Allow access to all objects for users with system-wide roles
    system_roles = ['ADMIN', 'INSPECTOR']
    user_groups = set(user.groups.values_list('name', flat=True))
    if user_groups & set(system_roles):
        return qs
    model = qs.model
    org_field = None
    object_field = None
    if any(f.name == "org" for f in model._meta.fields):
        org_field = "org_id"
    if any(f.name == "object" for f in model._meta.fields):
        object_field = "object_id"
    if not org_field and not object_field:
        return qs

    from django.db.models import Q

    q = Q()
    if org_field:
        org_ids = get_user_org_ids(user)
        q |= Q(**{f"{org_field}__in": org_ids})
    if object_field:
        obj_ids = get_user_object_ids(user)
        if obj_ids:
            q |= Q(**{f"{object_field}__in": obj_ids})
        # Fallback: доступ по членству в организации владельца объекта, даже если нет прямого назначения
        org_ids = get_user_org_ids(user)
        if org_ids:
            q |= Q(**{f"{object_field}__org_id__in": org_ids})
    return qs.filter(q).distinct()


class ScopedQuerySetMixin:
    """Mixin для ViewSet ограничивающий queryset объектным скоупом пользователя.

    Использование: разместить раньше GenericViewSet в списке наследования.
    Переопределяет get_queryset и применяет scope_qs_to_user.
    """

    def get_queryset(self):  # type: ignore[override]
        base_qs = super().get_queryset()  # type: ignore
        user = getattr(self.request, "user", None)
        if user is None:
            return base_qs.none()
        return scope_qs_to_user(base_qs, user)

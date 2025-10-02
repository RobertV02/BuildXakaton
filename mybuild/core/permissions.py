"""DRF permission классы (скелеты) для матрицы доступа.

Каждый класс содержит минимальную логику + TODO для дальнейшего наполнения
при реализации бизнес-флоу.
"""
from __future__ import annotations

from typing import Iterable, Optional
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from core.services.scoping import get_user_org_ids, get_user_object_ids


def _get_role_for_object(user: User, obj) -> Optional[str]:  # helper
    # Пытаемся найти роль пользователя относительно объекта
    from objects.models import ObjectAssignment
    if not user.is_authenticated:
        return None
    if hasattr(obj, 'object'):
        target_object = getattr(obj, 'object')
    else:
        target_object = obj
    try:
        assign = ObjectAssignment.objects.filter(
            user=user, object=target_object, is_active=True
        ).first()
        return assign.role if assign else None
    except Exception:
        return None


class IsOrgMember(BasePermission):
    message = 'Пользователь не входит в организацию ресурса.'

    def has_object_permission(self, request: Request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        org_id = getattr(obj, 'org_id', None)
        if org_id is None and hasattr(obj, 'object'):
            org_id = getattr(getattr(obj, 'object'), 'org_id', None)
        if org_id is None:
            return True  # нечего проверять
        return org_id in get_user_org_ids(request.user)


class IsObjectMember(BasePermission):
    message = 'Пользователь не назначен на объект.'

    def has_object_permission(self, request: Request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        object_id = getattr(obj, 'object_id', None)
        if object_id is None and hasattr(obj, 'object'):
            object_id = getattr(getattr(obj, 'object'), 'id', None)
        if object_id is None:
            return True
        return object_id in get_user_object_ids(request.user)


class HasObjectRole(BasePermission):
    """Проверяет что у пользователя одна из требуемых ролей на объекте.

    View может определить атрибут required_roles = ("client", "inspector", ...)
    """
    message = 'Недостаточная роль на объекте.'

    def has_object_permission(self, request: Request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        required = getattr(view, 'required_roles', None)
        if not required:
            return True
        role = _get_role_for_object(request.user, obj)
        return role in required


class StatePermission(BasePermission):
    """Проверяет статус FSM объекта перед действием.

    View/Action должен задать allowed_statuses = ( ... )
    """
    message = 'Недопустимый статус ресурса для операции.'

    def has_object_permission(self, request: Request, view, obj) -> bool:
        allowed = getattr(view, 'allowed_statuses', None)
        if not allowed:
            return True
        # Ищем поле status
        status = getattr(obj, 'status', None)
        if status is None:
            return True
        return status in allowed


class MatrixPermission(BasePermission):
    """Глобальная матрица прав по типу ресурса и действию.

    Пока упрощенно: для SAFE_METHODS разрешаем если пользователь член организации.
    Для mutating методов — проверяем роль (view.role_map: dict[str, Iterable[str]]).
    """
    message = 'Доступ запрещен согласно матрице ролей.'

    def has_permission(self, request: Request, view) -> bool:
        if request.user.is_superuser:
            return True
        # Для list/create у нас нет объекта — частичная проверка
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        # Fallback на стандартные model perms если нет role_map специфики
        model = None
        if hasattr(view, 'queryset') and getattr(view, 'queryset') is not None:
            try:
                model = view.queryset.model
            except Exception:
                model = None
        if model is None:
            try:
                model = view.get_queryset().model  # type: ignore[attr-defined]
            except Exception:
                model = None
        action = getattr(view, 'action', request.method.lower())
        if model is not None:
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            if request.method == 'POST':
                # detail custom POST actions (not create) should require change_*
                if action != 'create':
                    needed = f'{app_label}.change_{model_name}'
                else:
                    needed = f'{app_label}.add_{model_name}'
            elif request.method in ('PUT', 'PATCH'):
                needed = f'{app_label}.change_{model_name}'
            elif request.method == 'DELETE':
                needed = f'{app_label}.delete_{model_name}'
            else:
                needed = None
            if needed and not request.user.has_perm(needed):
                return False
        role_map = getattr(view, 'role_map', {})
        if not role_map:
            return True
        required_roles = role_map.get(action)
        if not required_roles:
            return True
        # Нужна хотя бы одна роль на любом доступном объекте
        # (детальная проверка будет в has_object_permission)
        from orgs.models import Membership
        user_roles = list(Membership.objects.filter(user=request.user).values_list('role', flat=True))
        return bool(set(required_roles) & set(user_roles)) or request.user.is_authenticated

    def has_object_permission(self, request: Request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return True
        role_map = getattr(view, 'role_map', {})
        action = getattr(view, 'action', request.method.lower())
        required_roles = role_map.get(action)
        if not required_roles:
            return True
        # Debug logging
        print(f"DEBUG MatrixPermission: action={action}, required_roles={required_roles}")
        role = _get_role_for_object(request.user, obj)
        print(f"DEBUG MatrixPermission: _get_role_for_object returned: {role}")
        if role in required_roles:
            print("DEBUG MatrixPermission: role found in required_roles")
            return True
        # Fallback: берем роли по членству в организации, если нет назначения на объект
        org_id = getattr(obj, 'org_id', None)
        if org_id is None and hasattr(obj, 'object'):
            try:
                org_id = getattr(getattr(obj, 'object'), 'org_id', None)
            except Exception:
                org_id = None
        print(f"DEBUG MatrixPermission: org_id={org_id}")
        if org_id is not None:
            try:
                from orgs.models import Membership
                membership_roles = set(Membership.objects.filter(user=request.user, org_id=org_id).values_list('role', flat=True))
                print(f"DEBUG MatrixPermission: membership_roles={membership_roles}")
                if membership_roles & set(required_roles):
                    print("DEBUG MatrixPermission: membership roles match")
                    return True
            except Exception as e:
                print(f"DEBUG MatrixPermission: membership check error: {e}")
        # Additional fallback: check Django groups if no membership found
        user_groups = set(request.user.groups.values_list('name', flat=True))
        print(f"DEBUG MatrixPermission: user_groups={user_groups}")
        if user_groups & set(required_roles):
            print("DEBUG MatrixPermission: django groups match")
            return True
        print("DEBUG MatrixPermission: no permission found")
        return False


class IsOnSite(BasePermission):
    """Проверяет что пользователь 'на площадке' (активный визит и координаты).

    Пока заглушка: просто проверяет наличие активного InspectionVisit на объект.
    """
    message = 'Нет активного визита на объекте или не подтверждено присутствие.'

    def has_permission(self, request: Request, view) -> bool:  # type: ignore[override]
        return True  # объектная проверка далее

    def has_object_permission(self, request: Request, view, obj) -> bool:  # type: ignore[override]
        from inspections.models import InspectionVisit
        from objects.models import ConstructionObject
        if request.user.is_superuser:
            return True
        # Resolve object instance
        construction_object = None
        if isinstance(obj, ConstructionObject):
            construction_object = obj
        elif hasattr(obj, 'object'):
            construction_object = getattr(obj, 'object')
        if construction_object is None:
            return True  # nothing to check
        # Active visit for user
        visit = (
            InspectionVisit.objects.filter(
                object=construction_object, inspector=request.user, ended_at__isnull=True
            )
            .order_by('-started_at')
            .first()
        )
        if not visit:
            return False
        # If no coordinates skip geo constraint
        if visit.latitude is None or visit.longitude is None:
            return True
        polygon = getattr(construction_object, 'polygon', None)
        if not polygon:
            return True
        try:
            if polygon.get('type') != 'Polygon':
                return True
            rings = polygon.get('coordinates') or []
            if not rings:
                return True
            outer = rings[0]
            return _point_in_polygon(visit.longitude, visit.latitude, outer)
        except Exception:
            return True


def _point_in_polygon(x: float, y: float, polygon) -> bool:
    """Ray casting algorithm for point inclusion in simple polygon.

    polygon: list of [x,y]. Assumes first==last maybe; we ignore last duplicate.
    """
    inside = False
    n = len(polygon)
    if n < 3:
        return True
    for i in range(n - 1):
        x1, y1 = polygon[i]
        x2, y2 = polygon[i + 1]
        intersects = ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1
        )
        if intersects:
            inside = not inside
    return inside

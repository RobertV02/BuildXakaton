from django.contrib.auth.models import User
from functools import lru_cache

ROLE_CLIENT = "CLIENT"
ROLE_FOREMAN = "FOREMAN"
ROLE_INSPECTOR = "INSPECTOR"
ROLE_ADMIN = "ADMIN"

ROLE_ATTRS = {
    ROLE_CLIENT: "is_client",
    ROLE_FOREMAN: "is_foreman",
    ROLE_INSPECTOR: "is_inspector",
    ROLE_ADMIN: "is_admin",
}

@lru_cache(maxsize=512)
def _user_group_names(user_id: int, version: int):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return set()
    return set(user.groups.values_list("name", flat=True))

def _has_role(user: User, role: str) -> bool:
    if user.is_superuser:
        return True
    groups = _user_group_names(user.id, int(user.last_login.timestamp()) if user.last_login else 0)
    return role in groups

def is_client(user: User) -> bool:
    return _has_role(user, ROLE_CLIENT)

def is_foreman(user: User) -> bool:
    return _has_role(user, ROLE_FOREMAN)

def is_inspector(user: User) -> bool:
    return _has_role(user, ROLE_INSPECTOR)

def is_admin(user: User) -> bool:
    return _has_role(user, ROLE_ADMIN)

__all__ = [
    "is_client",
    "is_foreman",
    "is_inspector",
    "is_admin",
]

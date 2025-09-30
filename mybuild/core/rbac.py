"""RBAC auto-synchronization logic.

This module listens to Django's post_migrate signal and ensures that
ROLE_GROUPS and MODEL_PERMS_MAP are reflected in the database even if
data migrations were skipped on a target server.
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .permissions_config import ROLE_GROUPS, MODEL_PERMS_MAP


@receiver(post_migrate)
def ensure_rbac(sender, **kwargs):  # type: ignore[override]
    """Ensure groups and their permissions exist after migrations.

    This is idempotent; it only adds missing permissions and groups.
    It does NOT remove permissions that were manually added later.
    """
    # Create groups
    for code, _label in ROLE_GROUPS.items():
        Group.objects.get_or_create(name=code)

    # Assign permissions
    for model_label, role_perms in MODEL_PERMS_MAP.items():
        try:
            app_label, model_name = model_label.split('.')
        except ValueError:
            continue
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            continue
        for group_name, perm_codenames in role_perms.items():
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                continue
            for codename in perm_codenames:
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                except Permission.DoesNotExist:
                    continue
                group.permissions.add(perm)
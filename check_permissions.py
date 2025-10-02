#!/usr/bin/env python3
"""
Check Django permissions for user nkains
"""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User
from objects.models import ConstructionObject

# Get the user
user = User.objects.get(username='nkains')
print(f"User: {user.username}")
print(f"Is superuser: {user.is_superuser}")
print(f"Is staff: {user.is_staff}")

# Check Django permissions
perms_to_check = [
    'objects.add_constructionobject',
    'objects.change_constructionobject',
    'objects.delete_constructionobject',
    'objects.view_constructionobject',
]

print("\nDjango permissions:")
for perm in perms_to_check:
    has_perm = user.has_perm(perm)
    print(f"  {perm}: {has_perm}")

# Check user permissions
print(f"\nUser permissions: {list(user.user_permissions.all())}")
print(f"Groups: {list(user.groups.all())}")

# Check if user has any permissions via groups
print("\nGroup permissions:")
for group in user.groups.all():
    print(f"  Group '{group.name}': {list(group.permissions.all())}")

# Check all permissions the user has
all_perms = user.get_all_permissions()
print(f"\nAll user permissions: {sorted(all_perms)}")
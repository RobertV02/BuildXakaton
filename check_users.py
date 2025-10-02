#!/usr/bin/env python
import os
import sys

# Add project path
sys.path.insert(0, os.path.dirname(__file__))

import django
os.environ['DJANGO_SETTINGS_MODULE']='mybuild.settings'
django.setup()
from django.contrib.auth.models import User, Group
from orgs.models import Membership

# Проверим всех пользователей с группой INSPECTOR
inspectors = User.objects.filter(groups__name='INSPECTOR')
print('Users with INSPECTOR group:')
for user in inspectors:
    print(f'  {user.username}: {user.email}')
    memberships = Membership.objects.filter(user=user)
    print(f'    Memberships: {[f"{m.org.name}: {m.role}" for m in memberships]}')

# Проверим всех пользователей с ролью INSPECTOR в Membership
inspector_memberships = Membership.objects.filter(role='INSPECTOR')
print('\nUsers with INSPECTOR role in Membership:')
for m in inspector_memberships:
    print(f'  {m.user.username}: {m.org.name}')
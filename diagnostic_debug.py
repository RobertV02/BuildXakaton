#!/usr/bin/env python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mybuild.settings')
django.setup()

from django.contrib.auth.models import User
from objects.models import ConstructionObject
from orgs.models import Membership
from rest_framework.test import APIClient

print("=== DIAGNOSTIC: Inspector Activation Issue ===\n")

# Найдем объект в ACTIVATION_PENDING
try:
    obj = ConstructionObject.objects.filter(status='ACTIVATION_PENDING').first()
    if not obj:
        print('ERROR: No object in ACTIVATION_PENDING status')
        exit()
    print(f'Object: {obj.name} (ID: {obj.pk}) - Status: {obj.status}')
    print(f'Object org: {obj.org.name}')
except Exception as e:
    print(f'ERROR finding object: {e}')
    exit()

# Проверим всех инспекторов
inspectors = User.objects.filter(groups__name='INSPECTOR')
print(f'\nFound {len(inspectors)} users with INSPECTOR group:')
for user in inspectors:
    print(f'  User: {user.username} ({user.email})')

    # Проверим memberships
    memberships = Membership.objects.filter(user=user)
    print(f'    Memberships: {[f"{m.org.name}: {m.role}" for m in memberships]}')

    # Проверим Django groups
    groups = user.groups.values_list('name', flat=True)
    print(f'    Django groups: {list(groups)}')

    # Тестируем API
    client = APIClient()
    client.force_authenticate(user=user)
    try:
        print(f'    Testing API call...')
        response = client.post(f'/api/objects/{obj.pk}/activate/')
        print(f'    API activate result: {response.status_code}')
        if response.status_code != 200:
            print(f'    Error: {response.data}')
    except Exception as e:
        print(f'    API error: {e}')
    print()

print("=== END DIAGNOSTIC ===")
#!/usr/bin/env python3
"""
Final test of the permission fix
"""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from objects.models import ConstructionObject

print("=== FINAL PERMISSION FIX TEST ===")

# Get test user and object
user = User.objects.get(username='nkains')
obj = ConstructionObject.objects.get(name='test')

print(f"User: {user.username}")
print(f"Object: {obj.name} (ID: {obj.pk})")
print(f"Object status: {obj.status}")

# Test the API call
client = APIClient()
client.force_authenticate(user=user)

print("\nTesting activate action...")
response = client.post(f'/api/objects/{obj.pk}/activate/')

print(f"Response status: {response.status_code}")
if response.status_code == 200:
    print("✅ SUCCESS: Activate action worked!")
    obj.refresh_from_db()
    print(f"New object status: {obj.status}")
else:
    print(f"❌ FAILED: {response.content.decode()}")

print("\n=== TEST COMPLETE ===")
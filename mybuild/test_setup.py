#!/usr/bin/env python
"""
Test script to create test users with different roles and test object lifecycle.
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from orgs.models import Organization, Membership, RoleType
from objects.models import ConstructionObject, ObjectStatus
from core.permissions_config import ROLE_GROUPS
import json


def create_test_data():
    print("Создание тестовых данных...")

    # 1. Создаем тестовую организацию
    org, created = Organization.objects.get_or_create(
        name="Тестовая организация",
        defaults={'description': 'Организация для тестирования'}
    )
    print(f"Организация: {org.name} ({'создана' if created else 'уже существует'})")

    # 2. Создаем Django группы
    groups = {}
    for role_code, role_name in ROLE_GROUPS.items():
        group, created = Group.objects.get_or_create(name=role_code)
        groups[role_code] = group
        print(f"Группа: {role_code} ({'создана' if created else 'уже существует'})")

    # 3. Создаем тестовых пользователей
    test_users = [
        ('test_admin', 'Администратор', 'ADMIN', RoleType.ADMIN),
        ('test_client', 'Заказчик', 'CLIENT', RoleType.CLIENT),
        ('test_foreman', 'Прораб', 'FOREMAN', RoleType.FOREMAN),
        ('test_inspector', 'Инспектор', 'INSPECTOR', RoleType.INSPECTOR),
    ]

    users = {}
    for username, full_name, group_name, membership_role in test_users:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@test.com',
                'first_name': full_name,
                'is_active': True
            }
        )
        if created:
            user.set_password('test123')
            user.save()

        # Добавляем в Django группу
        user.groups.add(groups[group_name])

        # Создаем membership в организации
        membership, created = Membership.objects.get_or_create(
            org=org,
            user=user,
            role=membership_role
        )

        users[username] = user
        print(f"Пользователь: {username} ({'создан' if created else 'уже существует'}) - роль: {membership_role}")

    # 4. Создаем тестовый объект
    test_object, created = ConstructionObject.objects.get_or_create(
        name="Тестовый строительный объект",
        org=org,
        defaults={
            'description': 'Объект для тестирования жизненного цикла',
            'polygon': [],  # Пустой массив координат
            'status': ObjectStatus.DRAFT,
        }
    )
    print(f"Объект: {test_object.name} ({'создан' if created else 'уже существует'}) - статус: {test_object.status}")

    return org, users, test_object


def test_object_lifecycle(users, test_object):
    print("\nТестирование жизненного цикла объекта...")

    from rest_framework.test import APIClient

    # Тест 1: Планирование (CLIENT)
    print(f"1. Текущий статус: {test_object.status}")
    print("   Тестируем планирование (CLIENT)...")

    client = APIClient()
    client.force_authenticate(user=users['test_client'])
    response = client.post(f'/api/objects/{test_object.pk}/plan/')

    if response.status_code == 200:
        test_object.refresh_from_db()
        print(f"   ✓ Планирование успешно: {test_object.status}")
    else:
        print(f"   ✗ Ошибка планирования: {response.status_code} - {response.content.decode()}")

    # Тест 2: Запрос активации (CLIENT)
    print("   Тестируем запрос активации (CLIENT)...")

    client = APIClient()
    client.force_authenticate(user=users['test_client'])
    response = client.post(f'/api/objects/{test_object.pk}/request_activation/')

    if response.status_code == 200:
        test_object.refresh_from_db()
        print(f"   ✓ Запрос активации успешен: {test_object.status}")
    else:
        print(f"   ✗ Ошибка запроса активации: {response.status_code} - {response.content.decode()}")

    # Тест 3: Активация (INSPECTOR)
    print("   Тестируем активацию (INSPECTOR)...")

    # Проверим memberships для инспектора
    inspector_memberships = users['test_inspector'].memberships.all()
    print(f"     Memberships для инспектора: {[f'{m.role} in {m.org.name}' for m in inspector_memberships]}")

    client = APIClient()
    client.force_authenticate(user=users['test_inspector'])
    response = client.post(f'/api/objects/{test_object.pk}/activate/')

    if response.status_code == 200:
        test_object.refresh_from_db()
        print(f"   ✓ Активация успешна: {test_object.status}")

        # Проверяем, создался ли opening checklist
        if hasattr(test_object, 'opening_checklist'):
            print("   ✓ Автоматически создан opening checklist")
        else:
            print("   ✗ Opening checklist не создан")
    else:
        print(f"   ✗ Ошибка активации: {response.status_code} - {response.content.decode()}")

    # Тест 4: Закрытие (ADMIN)
    print("   Тестируем закрытие (ADMIN)...")

    # Проверим memberships для админа
    admin_memberships = users['test_admin'].memberships.all()
    print(f"     Memberships для админа: {[f'{m.role} in {m.org.name}' for m in admin_memberships]}")

    client = APIClient()
    client.force_authenticate(user=users['test_admin'])
    response = client.post(f'/api/objects/{test_object.pk}/close/')

    if response.status_code == 200:
        test_object.refresh_from_db()
        print(f"   ✓ Закрытие успешно: {test_object.status}")
    else:
        print(f"   ✗ Ошибка закрытия: {response.status_code} - {response.content.decode()}")


def test_permissions():
    print("\nТестирование прав доступа...")

    from rest_framework.test import APIClient

    # Создаем тестовый объект для проверки
    org = Organization.objects.filter(name="Тестовая организация").first()
    if not org:
        print("   ✗ Тестовая организация не найдена")
        return

    test_obj = ConstructionObject.objects.filter(org=org).first()
    if not test_obj:
        print("   ✗ Тестовый объект не найден")
        return

    # Сбрасываем статус для тестирования
    test_obj.status = ObjectStatus.DRAFT
    test_obj.save()

    # Тест: неавторизованный пользователь
    print("   Тестируем неавторизованного пользователя...")
    client = APIClient()
    response = client.post(f'/api/objects/{test_obj.pk}/plan/')
    if response.status_code == 401:
        print("   ✓ Неавторизованный пользователь заблокирован")
    else:
        print(f"   ✗ Неавторизованный пользователь прошел: {response.status_code}")

    # Тест: неправильная роль (FOREMAN пытается планировать)
    print("   Тестируем неправильную роль (FOREMAN планирует)...")
    foreman_user = User.objects.filter(username='test_foreman').first()
    if foreman_user:
        client = APIClient()
        client.force_authenticate(user=foreman_user)
        response = client.post(f'/api/objects/{test_obj.pk}/plan/')
        if response.status_code == 403:
            print("   ✓ FOREMAN правильно заблокирован для планирования")
        else:
            print(f"   ✗ FOREMAN прошел планирование: {response.status_code}")

    # Тест: правильная роль (CLIENT планирует)
    print("   Тестируем правильную роль (CLIENT планирует)...")
    client_user = User.objects.filter(username='test_client').first()
    if client_user:
        client = APIClient()
        client.force_authenticate(user=client_user)
        response = client.post(f'/api/objects/{test_obj.pk}/plan/')
        if response.status_code == 200:
            print("   ✓ CLIENT правильно прошел планирование")
        else:
            print(f"   ✗ CLIENT заблокирован для планирования: {response.status_code} - {response.content.decode()}")


if __name__ == '__main__':
    try:
        org, users, test_object = create_test_data()
        test_object_lifecycle(users, test_object)
        test_permissions()

        print("\nТестирование завершено!")
        print("\nТестовые учетные записи:")
        for username, user in users.items():
            print(f"  {username}: {user.first_name} - пароль: test123")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
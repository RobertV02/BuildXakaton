"""Команда инициализации ролей и разрешений.

Запускать после миграций: создаёт/обновляет группы и назначает
им разрешения согласно матрице.

Команда идемпотентна: повторный запуск не создает дубликатов.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.permissions_config import ROLE_GROUPS, MODEL_PERMS_MAP


class Command(BaseCommand):
    help = 'Создает группы и назначает им разрешения согласно матрице.'

    def handle(self, *args, **options):  # type: ignore[override]
        self.stdout.write('Инициализация групп...')
        groups = {}
        for code, _label in ROLE_GROUPS.items():
            group, _ = Group.objects.get_or_create(name=code)
            groups[code] = group
        self.stdout.write(self.style.SUCCESS('Группы готовы.'))

        self.stdout.write('Назначение разрешений...')
        for model_label, role_perms in MODEL_PERMS_MAP.items():
            app_label, model_name = model_label.split('.')
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                self.stderr.write(f'ContentType не найден: {model_label}')
                continue
            for group_name, perm_codenames in role_perms.items():
                group = groups.get(group_name)
                if not group:
                    continue
                for codename in perm_codenames:
                    try:
                        perm = Permission.objects.get(content_type=ct, codename=codename)
                    except Permission.DoesNotExist:
                        self.stderr.write(f' ! Разрешение {codename} не найдено для {model_label}')
                        continue
                    group.permissions.add(perm)
        self.stdout.write(self.style.SUCCESS('Разрешения назначены.'))
        self.stdout.write(self.style.SUCCESS('init_roles_permissions: OK'))
"""Команда инициализации ролей и разрешений.

Запускать после миграций: создаёт/обновляет группы и назначает
им разрешения согласно матрице.

Команда идемпотентна: повторный запуск не создает дубликатов.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

ROLE_GROUPS = {
    'ORG_ADMIN': 'Администратор организации',
    'CLIENT': 'Заказчик',
    'FOREMAN': 'Прораб',
    'INSPECTOR': 'Инспектор',
}


MODEL_PERMS_MAP = {
    # model_label: {group: [codename,..]}
    'objects.constructionobject': {
        'CLIENT': ['add_constructionobject', 'change_constructionobject', 'delete_constructionobject', 'view_constructionobject', 'can_confirm_geozone'],
        'FOREMAN': ['view_constructionobject'],
        'INSPECTOR': ['view_constructionobject', 'can_confirm_geozone'],
    },
    # OpeningChecklist permissions:
    # - FOREMAN: full CRUD (add, change, delete, view)
    # - CLIENT & INSPECTOR: create, view, update only (no delete)
    'objects.openingchecklist': {
        'CLIENT': ['add_openingchecklist', 'change_openingchecklist', 'view_openingchecklist'],
        'FOREMAN': ['add_openingchecklist', 'change_openingchecklist', 'delete_openingchecklist', 'view_openingchecklist'],
        'INSPECTOR': ['add_openingchecklist', 'change_openingchecklist', 'view_openingchecklist'],
    },
    'schedules.workitem': {
        'CLIENT': ['add_workitem', 'change_workitem', 'delete_workitem', 'view_workitem'],
        'FOREMAN': ['view_workitem', 'can_set_actual'],
        'INSPECTOR': ['view_workitem'],
    },
    'materials.ocrresult': {
        'FOREMAN': ['can_run_ocr', 'view_ocrresult'],
        'INSPECTOR': ['can_validate_ttn', 'view_ocrresult'],
        'CLIENT': ['can_approve_ttn', 'view_ocrresult'],
    },
    'issues.remark': {
        'CLIENT': ['add_remark', 'change_remark', 'view_remark', 'can_comment_issue', 'can_close_issue'],
        'INSPECTOR': ['view_remark', 'can_comment_issue', 'can_verify_issue'],
        'FOREMAN': ['view_remark', 'can_comment_issue'],
    },
    'issues.violation': {
        'INSPECTOR': ['add_violation', 'change_violation', 'view_violation', 'can_comment_issue', 'can_close_issue'],
        'CLIENT': ['view_violation', 'can_comment_issue', 'can_verify_issue'],
        'FOREMAN': ['view_violation', 'can_comment_issue'],
    },
    'audit.auditlog': {
        'CLIENT': ['can_view_auditlog', 'view_auditlog'],
        'INSPECTOR': ['can_view_auditlog', 'view_auditlog'],
    },
}


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
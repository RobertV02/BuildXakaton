# Permissions Management

Права пользователей теперь управляются через файлы и автоматически применяются при деплое.

## Структура

- `core/permissions_config.py` - конфигурация прав для всех ролей
- `core/migrations/0001_setup_permissions.py` - миграция, которая применяет права
- `core/management/commands/init_roles_permissions.py` - команда для ручного применения прав

## Как изменить права

1. Отредактируйте `core/permissions_config.py`
2. Создайте новую миграцию: `python manage.py makemigrations --empty core --name update_permissions_YYYYMMDD`
3. Заполните миграцию аналогично `0001_setup_permissions.py`
4. Закоммитьте изменения
5. На сервере: `python manage.py migrate`

## Пример изменения прав

```python
# В core/permissions_config.py
MODEL_PERMS_MAP = {
    'objects.openingchecklist': {
        'CLIENT': ['add_openingchecklist', 'change_openingchecklist', 'delete_openingchecklist', 'view_openingchecklist'],
        'FOREMAN': ['view_openingchecklist'],
        'INSPECTOR': ['view_openingchecklist'],  # Только просмотр
    },
}
```

## Автоматическое применение

При деплое на сервер права автоматически применяются через миграции Django. Ручной запуск `init_roles_permissions` больше не требуется для новых серверов.
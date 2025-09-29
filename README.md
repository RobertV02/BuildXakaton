# MyBuild Backend

## Ключевые возможности
- RBAC + матричные роли (MatrixPermission)
- Скоуп по организациям/объектам
- FSM экшены для ConstructionObject и OpeningChecklist
- Offline идемпотентность по `offline_batch_id`
- Аудит действий (AuditLog) + уведомления (Notification)
- Geo присутствие (IsOnSite)
- OpenAPI схема (drf-spectacular)

## OpenAPI / Документация
Маршруты:
- `/api/schema/` — JSON/YAML OpenAPI 3.0 (по умолчанию JSON)
- `/api/docs/` — Swagger UI
- `/api/redoc/` — ReDoc

Генерация файла:
```
python manage.py generate_schema --file schema.yaml
```
Файл `schema.yaml` можно коммитить для фиксации версии.

## Offline Idempotency
POST `/api/deliveries/` с одинаковым `offline_batch_id`:
- Первая отправка -> 201 Created + аудит `create_delivery`
- Повтор -> 200 OK + аудит `replay_delivery`

## FSM Actions (примеры)
```
POST /api/objects/{id}/plan/
POST /api/objects/{id}/request_activation/
POST /api/objects/{id}/activate/
POST /api/objects/{id}/close/

POST /api/opening-checklists/{id}/submit/
POST /api/opening-checklists/{id}/approve/
POST /api/opening-checklists/{id}/reject/ {"comment": "..."}
```
Каждый переход логируется в AuditLog и порождает Notification.

## Тесты
Запуск всех тестов:
```
python manage.py test -v 2
```

## Быстрый старт (dev)
```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Инициалиация ролей
```
python manage.py init_roles_permissions
```

## Контакты
Поддержка: support@example.com

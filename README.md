# Alpha Build - Система контроля качества строительства

Система для управления строительными объектами, контроля качества работ и документооборота в строительной отрасли.

## 🚀 Ключевые возможности

### 📍 Управление объектами строительства
- Создание и управление строительными объектами
- **Интерактивное картографирование** с поддержкой полигонов зон объектов
- Интеграция с MapLibre GL JS для рисования и отображения полигонов
- Геокодирование адресов через Nominatim API

### 📋 Контроль качества
- Чек-листы активации объектов
- Ежедневные чек-листы контроля
- FSM (Finite State Machine) для управления статусами
- Матричные роли и разрешения (RBAC)

### 👥 Управление пользователями
- Ролевая модель: Администратор, Инспектор, Прораб, Клиент
- Скоуп по организациям и объектам
- Аудит всех действий пользователей

### 📊 Аналитика и отчетность
- Аудит-лог всех операций
- Система уведомлений
- Отчеты по объектам и чек-листам

### 🔧 Технические возможности
- REST API с OpenAPI 3.0 документацией
- Offline-поддержка с идемпотентностью
- Docker-контейнеризация
- PostgreSQL с PostGIS для геоданных

## 🛠 Технологии

- **Backend**: Django 5.2.6 + Django REST Framework
- **База данных**: PostgreSQL + PostGIS
- **API документация**: drf-spectacular (OpenAPI 3.0)
- **Картография**: MapLibre GL JS
- **Геокодирование**: Nominatim API
- **Кеширование**: Redis
- **Деплой**: Docker + Docker Compose
- **Фронтенд**: HTML/CSS/JavaScript (Vanilla)

## 📋 Быстрый старт (разработка)

### Предварительные требования
- Python 3.10+
- PostgreSQL с PostGIS
- Redis (опционально)
- Git

### Установка и запуск

1. **Клонирование репозитория**
```bash
git clone <URL_РЕПОЗИТОРИЯ>
cd BuildXakaton
```

2. **Создание виртуального окружения**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**
Создайте файл `.env`:
```env
DJANGO_SECRET_KEY=ваш_секретный_ключ_здесь
POSTGRES_DB=buildnadz
POSTGRES_USER=buildnadz_user
POSTGRES_PASSWORD=buildnadz_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

5. **Миграции базы данных**
```bash
cd mybuild
python manage.py migrate
```

6. **Инициализация ролей и разрешений**
```bash
python manage.py init_roles_permissions
```

7. **Создание суперпользователя**
```bash
python manage.py createsuperuser
```

8. **Запуск сервера разработки**
```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

## 🐳 Развертывание с Docker

Для развертывания в закрытом контуре используйте Docker:

```bash
# Сборка и запуск
docker-compose up --build -d

# Применение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```

Подробные инструкции по развертыванию см. в [`deployment_instructions.md`](deployment_instructions.md).

## 📚 API Документация

### OpenAPI Спецификация
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **JSON схема**: `/api/schema/`

### Генерация схемы
```bash
python manage.py spectacular --file schema.yaml
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
python manage.py test -v 2

# Запуск с покрытием
coverage run manage.py test
coverage report
```

## 🔐 Аутентификация и авторизация

Система использует токеновую аутентификацию. Доступные роли:
- **Администратор**: Полный доступ ко всем функциям
- **Инспектор**: Контроль качества, утверждение чек-листов
- **Прораб**: Управление объектами, создание чек-листов
- **Клиент**: Просмотр объектов и отчетов

## 🗺 Картографические возможности

### Создание объектов
- Интерактивное рисование полигонов на карте
- Автоматическое геокодирование адресов
- Сохранение геометрии в формате GeoJSON

### Просмотр объектов
- Отображение полигонов зон объектов
- Автоматическое центрирование и масштабирование
- Навигационные элементы управления

## 📝 Основные API эндпоинты

### Объекты строительства
```
GET    /api/objects/          # Список объектов
POST   /api/objects/          # Создание объекта
GET    /api/objects/{id}/     # Детали объекта
PUT    /api/objects/{id}/     # Обновление объекта
DELETE /api/objects/{id}/     # Удаление объекта

# FSM действия
POST   /api/objects/{id}/plan/
POST   /api/objects/{id}/request_activation/
POST   /api/objects/{id}/activate/
POST   /api/objects/{id}/close/
```

### Чек-листы
```
GET    /api/checklists/       # Список чек-листов
POST   /api/checklists/       # Создание чек-листа
GET    /api/checklists/{id}/  # Детали чек-листа

# FSM действия
POST   /api/checklists/{id}/submit/
POST   /api/checklists/{id}/approve/
POST   /api/checklists/{id}/reject/
```

### Поставки материалов
```
GET    /api/deliveries/       # Список поставок
POST   /api/deliveries/       # Создание поставки (с offline_batch_id)
```

## 🔍 Мониторинг и логи

### Аудит-лог
Все действия пользователей логируются в `AuditLog` с указанием:
- Пользователя
- Действия
- Объекта
- Времени
- Дополнительных данных

### Уведомления
Система автоматически создает уведомления при:
- Изменении статуса объектов
- Утверждении/отклонении чек-листов
- Новых поставках материалов

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для вашей фичи (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Создайте Pull Request

## 📞 Контакты

- **Поддержка**: support@example.com
- **Документация**: [API Docs](/api/docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

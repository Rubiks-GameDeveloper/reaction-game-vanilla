# Быстрый старт

## Локальная разработка

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

2. **Создайте файл `.env`:**
```bash
# Скопируйте содержимое из ENV_EXAMPLE.txt в .env
# Или используйте команду (Linux/Mac):
cp ENV_EXAMPLE.txt .env

# Windows PowerShell:
Copy-Item ENV_EXAMPLE.txt .env
```

3. **Настройте базу данных PostgreSQL:**
   - Убедитесь, что PostgreSQL установлен и запущен
   - Создайте базу данных `reaction_game_db`
   - Обновите настройки в `.env` файле

4. **Примените миграции:**
```bash
python manage.py migrate
```

5. **Создайте суперпользователя:**
```bash
python manage.py createsuperuser
```

6. **Запустите сервер:**
```bash
python manage.py runserver
```

Сервер будет доступен по адресу: http://localhost:8000
Админ-панель: http://localhost:8000/admin/

## Docker

1. **Создайте файл `.env`:**
```bash
cp ENV_EXAMPLE.txt .env
```

2. **Запустите контейнеры:**
```bash
docker-compose up --build
```

3. **Создайте суперпользователя:**
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Остановка:**
```bash
docker-compose down
```

## Тестирование API

### Регистрация пользователя
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'
```

### Вход в систему
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### Сохранение игровой сессии (требует токен)
```bash
curl -X POST http://localhost:8000/api/games/sessions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "game_state": {"level": 1},
    "score": 1000,
    "difficulty": "medium",
    "time_played": 60,
    "is_completed": true,
    "reaction_times": [250, 300, 280]
  }'
```

### Получение таблицы лидеров
```bash
curl http://localhost:8000/api/games/leaderboard/
```

## Структура проекта

```
backend/
├── accounts/          # Приложение для пользователей и аутентификации
│   ├── models.py      # Модель User
│   ├── views.py       # API views для регистрации/логина
│   ├── serializers.py # Сериализаторы
│   └── urls.py        # URL маршруты
├── games/             # Приложение для игр
│   ├── models.py      # Модели: GameSession, Leaderboard, Achievement, Friendship
│   ├── views.py       # API views для игр
│   ├── serializers.py # Сериализаторы
│   ├── admin.py       # Админ-панель с экспортом XLSX
│   ├── signals.py     # Сигналы для автоматического создания профилей
│   └── urls.py        # URL маршруты
├── reaction_game/     # Основные настройки проекта
│   ├── settings.py    # Настройки Django
│   └── urls.py        # Главные URL маршруты
├── manage.py          # Django management script
├── requirements.txt   # Python зависимости
├── Dockerfile         # Docker образ
├── docker-compose.yml # Docker Compose конфигурация
└── README.md         # Полная документация
```


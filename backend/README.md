# Reaction Game Backend

Backend сервер для игры на реакцию на Django и Django REST Framework.

## Возможности

- ✅ Аутентификация с JWT токенами
- ✅ Профили пользователей с аватарами
- ✅ Сохранение и загрузка игровых сессий
- ✅ Таблица лидеров с фильтрацией
- ✅ Система достижений
- ✅ Система друзей
- ✅ Админ-панель с экспортом в XLSX
- ✅ PostgreSQL база данных
- ✅ Docker контейнеризация

## Установка и запуск

### Локальная разработка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Настройте базу данных PostgreSQL и обновите `.env` файл.

4. Выполните миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

### Docker

1. Создайте файл `.env`:
```bash
cp .env.example .env
```

2. Запустите контейнеры:
```bash
docker-compose up --build
```

3. Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

## API Endpoints

### Аутентификация

- `POST /api/auth/register/` - Регистрация пользователя
- `POST /api/auth/login/` - Вход в систему
- `POST /api/auth/token/refresh/` - Обновление токена
- `GET /api/auth/profile/` - Получить профиль
- `PUT /api/auth/profile/` - Обновить профиль
- `GET /api/auth/users/<username>/` - Публичный профиль пользователя

### Игры

- `GET /api/games/sessions/` - Список игровых сессий пользователя
- `POST /api/games/sessions/` - Сохранить игровую сессию
- `GET /api/games/sessions/latest/` - Последняя сессия
- `GET /api/games/leaderboard/` - Таблица лидеров
- `GET /api/games/leaderboard/top/` - Топ игроков
- `GET /api/games/achievements/` - Список достижений
- `GET /api/games/user-achievements/` - Достижения пользователя

### Друзья

- `GET /api/games/friends/` - Список запросов на дружбу
- `POST /api/games/friends/` - Отправить запрос на дружбу
- `POST /api/games/friends/<id>/accept/` - Принять запрос
- `POST /api/games/friends/<id>/reject/` - Отклонить запрос
- `GET /api/games/friends/friends/` - Список друзей

## Админ-панель

Доступна по адресу `/admin/` после создания суперпользователя.

### Функции админа:

- Управление пользователями
- Просмотр всех игровых сессий
- Экспорт игровых сессий в XLSX
- Назначение достижений вручную
- Модерация дружбы

## Модели данных

### UserProfile
- `user` - Связь с пользователем
- `avatar` - Аватар
- `bio` - О себе
- `date_of_birth` - Дата рождения

### GameSession
- `user` - Пользователь
- `game_state` - Состояние игры (JSON)
- `score` - Очки
- `difficulty` - Уровень сложности
- `time_played` - Время игры
- `is_completed` - Завершена ли игра
- `reaction_times` - Времена реакции
- `avg_reaction_time` - Среднее время реакции

### Leaderboard
- `user` - Пользователь
- `score` - Очки
- `rank` - Ранг
- `difficulty` - Уровень сложности
- `date_achieved` - Дата достижения

### Achievement
- `name` - Название
- `description` - Описание
- `icon` - Иконка
- `achievement_type` - Тип достижения
- `requirement` - Требования (JSON)
- `points` - Очки за достижение

### Friendship
- `from_user` - От пользователя
- `to_user` - К пользователю
- `status` - Статус (pending/accepted/rejected)

## Безопасность

- Пароли хранятся в виде хешей (Django встроенная система)
- Защита от SQL-инъекций (используется только ORM Django)
- Защита от XSS (экранирование данных в админке)
- JWT токены для аутентификации
- CORS настройки для фронтенда

## Технологии

- Django 5.0.1
- Django REST Framework 3.14.0
- PostgreSQL
- JWT Authentication
- Docker & Docker Compose
- openpyxl для экспорта в XLSX


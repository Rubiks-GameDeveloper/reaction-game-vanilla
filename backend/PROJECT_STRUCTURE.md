# Структура проекта Backend

## Описание

Backend сервер для игры на реакцию, разработанный на Django и Django REST Framework. Предоставляет REST API для клиентской части игры и административную панель для управления.

## Архитектура

### Приложения Django

#### 1. `accounts` - Управление пользователями
- **Модели:**
  - `User` - Кастомная модель пользователя (расширяет AbstractUser)
  
- **API Endpoints:**
  - `POST /api/auth/register/` - Регистрация
  - `POST /api/auth/login/` - Вход (JWT токены)
  - `POST /api/auth/token/refresh/` - Обновление токена
  - `GET/PUT /api/auth/profile/` - Профиль пользователя
  - `GET /api/auth/users/<username>/` - Публичный профиль

#### 2. `games` - Игровая логика
- **Модели:**
  - `TimeStampedModel` - Абстрактная базовая модель с timestamps
  - `UserProfile` - Профиль пользователя (avatar, bio, date_of_birth)
  - `GameSession` - Сохранение игровых сессий
  - `Leaderboard` - Таблица лидеров
  - `Achievement` - Достижения
  - `UserAchievement` - Связь пользователей и достижений
  - `Friendship` - Система друзей

- **API Endpoints:**
  - `GET/POST /api/games/sessions/` - Игровые сессии
  - `GET /api/games/sessions/latest/` - Последняя сессия
  - `GET /api/games/leaderboard/` - Таблица лидеров
  - `GET /api/games/leaderboard/top/` - Топ игроков
  - `GET /api/games/achievements/` - Список достижений
  - `GET /api/games/user-achievements/` - Достижения пользователя
  - `GET/POST /api/games/friends/` - Система друзей
  - `POST /api/games/friends/<id>/accept/` - Принять запрос
  - `POST /api/games/friends/<id>/reject/` - Отклонить запрос
  - `GET /api/games/friends/friends/` - Список друзей

## Уровни доступа

### Гость
- Просмотр таблицы лидеров
- Просмотр публичных профилей
- Просмотр списка достижений

### Авторизованный пользователь
- Сохранение/загрузка игрового прогресса
- Получение достижений
- Обновление профиля
- Участие в рейтинге
- Система друзей

### Администратор
- Полный доступ к Django Admin
- Управление пользователями
- Просмотр всех игровых сессий
- Экспорт данных в XLSX
- Назначение достижений вручную
- Модерация

## Безопасность

- ✅ Пароли хранятся в виде хешей (Django встроенная система)
- ✅ Защита от SQL-инъекций (используется только ORM Django)
- ✅ Защита от XSS (экранирование данных в админке)
- ✅ JWT токены для аутентификации
- ✅ CORS настройки
- ✅ Валидация данных через сериализаторы

## База данных

PostgreSQL с следующими основными таблицами:
- `accounts_user` - Пользователи
- `games_userprofile` - Профили
- `games_gamesession` - Игровые сессии
- `games_leaderboard` - Таблица лидеров
- `games_achievement` - Достижения
- `games_userachievement` - Достижения пользователей
- `games_friendship` - Дружба

## Дополнительные функции

### Система друзей
- Отправка запросов на дружбу
- Принятие/отклонение запросов
- Просмотр списка друзей
- Просмотр прогресса друзей

### Админ-панель
- Экспорт игровых сессий в XLSX
- Назначение достижений вручную
- Модерация пользователей
- Управление контентом

## Технологии

- Django 5.0.1
- Django REST Framework 3.14.0
- Django REST Framework Simple JWT 5.3.1
- PostgreSQL
- Docker & Docker Compose
- openpyxl (экспорт XLSX)
- django-cors-headers
- django-filter

## Развертывание

### Локально
1. Установить зависимости
2. Настроить PostgreSQL
3. Применить миграции
4. Создать суперпользователя
5. Запустить сервер

### Docker
1. Создать `.env` файл
2. Запустить `docker-compose up`
3. Создать суперпользователя

Подробные инструкции в `QUICKSTART.md` и `README.md`.


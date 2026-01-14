"""
Тесты для API views (представлений).
Проверяют HTTP-ответы, авторизацию, CRUD-операции.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from games.models import GameSession, Leaderboard, Achievement, Friendship

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для API клиента."""
    return APIClient()


@pytest.fixture
def create_user():
    """Фикстура для создания пользователя."""
    def make_user(username='testuser', email='test@example.com', password='testpass123'):
        return User.objects.create_user(username=username, email=email, password=password)
    return make_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Фикстура для аутентифицированного клиента."""
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.mark.django_db
class TestAuthenticationViews:
    """Тесты системы аутентификации."""
    
    def test_register_user(self, api_client):
        """Тест регистрации нового пользователя."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()
    
    def test_login_user(self, api_client, create_user):
        """Тест входа пользователя."""
        user = create_user(username='logintest', password='testpass123')
        
        data = {
            'username': 'logintest',
            'password': 'testpass123'
        }
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self, api_client):
        """Тест входа с неверными данными."""
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGameSessionViews:
    """Тесты для GameSession API."""
    
    def test_guest_cannot_create_session(self, api_client):
        """Гость не может создавать игровые сессии."""
        data = {
            'score': 1000,
            'difficulty': 'easy',
            'is_completed': True
        }
        response = api_client.post('/api/games/sessions/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_authenticated_user_can_create_session(self, authenticated_client):
        """Авторизованный пользователь может создавать сессии."""
        client, user = authenticated_client
        
        data = {
            'score': 1500,
            'difficulty': 'medium',
            'time_played': 60,
            'is_completed': True,
            'reaction_times': [200, 250, 300]
        }
        response = client.post('/api/games/sessions/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert GameSession.objects.filter(user=user).exists()
    
    def test_get_user_sessions(self, authenticated_client):
        """Получение списка сессий пользователя."""
        client, user = authenticated_client
        
        # Создаем несколько сессий
        GameSession.objects.create(user=user, score=100, difficulty='easy')
        GameSession.objects.create(user=user, score=200, difficulty='medium')
        
        response = client.get('/api/games/sessions/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
    
    def test_get_latest_session(self, authenticated_client):
        """Получение последней сессии пользователя."""
        client, user = authenticated_client
        
        GameSession.objects.create(user=user, score=100)
        latest = GameSession.objects.create(user=user, score=500)
        
        response = client.get('/api/games/sessions/latest/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['score'] == 500


@pytest.mark.django_db
class TestLeaderboardViews:
    """Тесты для Leaderboard API."""
    
    def test_guest_can_view_leaderboard(self, api_client, create_user):
        """Гость может просматривать таблицу лидеров."""
        user = create_user()
        Leaderboard.objects.create(user=user, score=1000, difficulty='easy', rank=1)
        
        response = api_client.get('/api/games/leaderboard/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
    
    def test_filter_leaderboard_by_difficulty(self, api_client, create_user):
        """Фильтрация таблицы лидеров по сложности."""
        user = create_user()
        Leaderboard.objects.create(user=user, score=1000, difficulty='easy')
        Leaderboard.objects.create(user=user, score=2000, difficulty='hard')
        
        response = api_client.get('/api/games/leaderboard/?difficulty=easy')
        
        assert response.status_code == status.HTTP_200_OK
        # Обработка как пагинированного, так и непагинированного ответа
        results = response.data['results'] if 'results' in response.data else response.data
        for entry in results:
            assert entry['difficulty'] == 'easy'


@pytest.mark.django_db
class TestAchievementViews:
    """Тесты для Achievement API."""
    
    def test_guest_can_view_achievements(self, api_client):
        """Гость может просматривать достижения."""
        Achievement.objects.create(
            name='Test Achievement',
            description='Test',
            achievement_type='score',
            requirement={'min_score': 100}
        )
        
        response = api_client.get('/api/games/achievements/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
    
    def test_get_user_achievements(self, authenticated_client):
        """Получение достижений пользователя."""
        client, user = authenticated_client
        
        response = client.get('/api/games/user-achievements/')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestFriendshipViews:
    """Тесты для Friendship API."""
    
    def test_search_users(self, authenticated_client, create_user):
        """Поиск пользователей."""
        client, user = authenticated_client
        other_user = create_user(username='searchme', email='search@test.com')
        
        response = client.get('/api/games/friends/search/?q=search')
        
        assert response.status_code == status.HTTP_200_OK
        assert any(u['username'] == 'searchme' for u in response.data)
    
    def test_send_friend_request(self, authenticated_client, create_user):
        """Отправка запроса в друзья."""
        client, user = authenticated_client
        friend = create_user(username='friend', email='friend@test.com')
        
        data = {'friend_identifier': 'friend'}
        response = client.post('/api/games/friends/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Friendship.objects.filter(from_user=user, to_user=friend).exists()
    
    def test_accept_friend_request(self, authenticated_client, create_user):
        """Принятие запроса в друзья."""
        client, user = authenticated_client
        requester = create_user(username='requester', email='req@test.com')
        
        # Создаем входящий запрос
        friendship = Friendship.objects.create(
            from_user=requester,
            to_user=user,
            status='pending'
        )
        
        response = client.post(f'/api/games/friends/{friendship.id}/accept/')
        
        assert response.status_code == status.HTTP_200_OK
        friendship.refresh_from_db()
        assert friendship.status == 'accepted'
    
    def test_view_friend_profile(self, authenticated_client, create_user):
        """Просмотр профиля друга."""
        client, user = authenticated_client
        friend = create_user(username='myfriend', email='myfriend@test.com')
        
        # Создаем дружбу
        Friendship.objects.create(from_user=user, to_user=friend, status='accepted')
        
        response = client.get(f'/api/games/friends/{friend.id}/profile/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'myfriend'


@pytest.mark.django_db
class TestAccessControl:
    """Тесты контроля доступа."""
    
    def test_guest_cannot_access_protected_endpoints(self, api_client):
        """Гость не имеет доступа к защищенным эндпоинтам."""
        protected_urls = [
            '/api/games/sessions/',
            '/api/games/friends/',
            '/api/auth/profile/',
        ]
        
        for url in protected_urls:
            response = api_client.get(url)
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_user_can_only_access_own_data(self, authenticated_client, create_user):
        """Пользователь может получить доступ только к своим данным."""
        client, user = authenticated_client
        other_user = create_user(username='other', email='other@test.com')
        
        # Создаем сессию другого пользователя
        other_session = GameSession.objects.create(user=other_user, score=999)
        
        # Пытаемся получить доступ
        response = client.get(f'/api/games/sessions/{other_session.id}/')
        
        # Должен вернуть только свои сессии
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

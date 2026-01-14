"""
Тесты для моделей приложения games.
Проверяют создание, связи, валидацию и временные метки.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from games.models import (
    UserProfile,
    GameSession,
    Leaderboard,
    Achievement,
    UserAchievement,
    Friendship
)

User = get_user_model()


@pytest.mark.django_db
class TestUserProfile:
    """Тесты модели UserProfile."""
    
    def test_create_user_profile(self):
        """Тест создания профиля пользователя."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        profile = user.profile
        profile.bio = 'Test bio'
        profile.date_of_birth = '1990-01-01'
        profile.save()
        
        assert profile.user == user
        assert profile.bio == 'Test bio'
        assert str(profile.date_of_birth) == '1990-01-01'
        assert profile.created_at is not None
        assert profile.updated_at is not None
    
    def test_profile_timestamps(self):
        """Проверка автоматического заполнения created_at и updated_at."""
        user = User.objects.create_user(username='user1', email='u1@test.com')
        profile = user.profile
        
        created_time = profile.created_at
        updated_time = profile.updated_at
        
        # Обновляем профиль
        profile.bio = 'Updated bio'
        profile.save()
        profile.refresh_from_db()
        
        assert profile.created_at == created_time  # created_at не меняется
        assert profile.updated_at > updated_time  # updated_at обновляется


@pytest.mark.django_db
class TestGameSession:
    """Тесты модели GameSession."""
    
    def test_create_game_session(self):
        """Тест создания игровой сессии."""
        user = User.objects.create_user(username='gamer', email='gamer@test.com')
        session = GameSession.objects.create(
            user=user,
            score=1000,
            difficulty='medium',
            time_played=60,
            is_completed=True,
            reaction_times=[200, 250, 180]
        )
        
        assert session.user == user
        assert session.score == 1000
        assert session.difficulty == 'medium'
        assert session.is_completed is True
        assert session.avg_reaction_time == 210.0
    
    def test_game_session_foreign_key(self):
        """Проверка связи ForeignKey с User."""
        user = User.objects.create_user(username='player', email='player@test.com')
        session1 = GameSession.objects.create(user=user, score=500)
        session2 = GameSession.objects.create(user=user, score=700)
        
        assert user.game_sessions.count() == 2
        assert session1 in user.game_sessions.all()
        assert session2 in user.game_sessions.all()
    
    def test_game_session_validation(self):
        """Тест валидации полей (score >= 0)."""
        user = User.objects.create_user(username='test', email='test@test.com')
        session = GameSession(user=user, score=-100)
        
        with pytest.raises(ValidationError):
            session.full_clean()


@pytest.mark.django_db
class TestLeaderboard:
    """Тесты модели Leaderboard."""
    
    def test_create_leaderboard_entry(self):
        """Тест создания записи в таблице лидеров."""
        user = User.objects.create_user(username='leader', email='leader@test.com')
        entry = Leaderboard.objects.create(
            user=user,
            score=5000,
            difficulty='hard',
            rank=1
        )
        
        assert entry.user == user
        assert entry.score == 5000
        assert entry.rank == 1
        assert entry.date_achieved is not None


@pytest.mark.django_db
class TestAchievement:
    """Тесты модели Achievement."""
    
    def test_create_achievement(self):
        """Тест создания достижения."""
        achievement = Achievement.objects.create(
            name='Новичок',
            description='Сыграйте 3 игры',
            achievement_type='games_played',
            requirement={'min_games': 3},
            points=0
        )
        
        assert achievement.name == 'Новичок'
        assert achievement.requirement['min_games'] == 3
        assert achievement.points == 0


@pytest.mark.django_db
class TestUserAchievement:
    """Тесты модели UserAchievement."""
    
    def test_user_achievement_relationship(self):
        """Проверка связи между пользователем и достижением."""
        user = User.objects.create_user(username='achiever', email='achiever@test.com')
        achievement = Achievement.objects.create(
            name='Test Achievement',
            description='Test',
            achievement_type='score',
            requirement={'min_score': 100}
        )
        
        user_achievement = UserAchievement.objects.create(
            user=user,
            achievement=achievement
        )
        
        assert user_achievement.user == user
        assert user_achievement.achievement == achievement
        assert user_achievement.unlocked_at is not None


@pytest.mark.django_db
class TestFriendship:
    """Тесты модели Friendship."""
    
    def test_create_friendship(self):
        """Тест создания запроса в друзья."""
        user1 = User.objects.create_user(username='user1', email='u1@test.com')
        user2 = User.objects.create_user(username='user2', email='u2@test.com')
        
        friendship = Friendship.objects.create(
            from_user=user1,
            to_user=user2,
            status='pending'
        )
        
        assert friendship.from_user == user1
        assert friendship.to_user == user2
        assert friendship.status == 'pending'
    
    def test_friendship_status_choices(self):
        """Проверка валидности статусов дружбы."""
        user1 = User.objects.create_user(username='a', email='a@test.com')
        user2 = User.objects.create_user(username='b', email='b@test.com')
        
        # Валидные статусы
        for status in ['pending', 'accepted', 'rejected']:
            friendship = Friendship.objects.create(
                from_user=user1,
                to_user=user2,
                status=status
            )
            assert friendship.status == status
            friendship.delete()

"""
Models for the reaction game application.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()


class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at timestamps.
    All models should inherit from this model.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):
    """
    Extended user profile with additional information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='О себе'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'


class GameSession(TimeStampedModel):
    """
    Game session save/load model.
    Stores game state, score, level, and other game-related data.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Легкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='game_sessions',
        verbose_name='Пользователь'
    )
    game_state = models.JSONField(
        default=dict,
        verbose_name='Состояние игры',
        help_text='JSON объект с данными о состоянии игры'
    )
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Очки'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='easy',
        verbose_name='Уровень сложности'
    )
    time_played = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Время игры (секунды)'
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Игра завершена'
    )
    reaction_times = models.JSONField(
        default=list,
        verbose_name='Времена реакции',
        help_text='Список времен реакции в миллисекундах'
    )
    avg_reaction_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Среднее время реакции (мс)'
    )

    class Meta:
        verbose_name = 'Игровая сессия'
        verbose_name_plural = 'Игровые сессии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Сессия {self.user.username} - {self.score} очков ({self.difficulty})'

    def save(self, *args, **kwargs):
        # Calculate average reaction time if reaction_times is provided
        if self.reaction_times and isinstance(self.reaction_times, list) and len(self.reaction_times) > 0:
            self.avg_reaction_time = sum(self.reaction_times) / len(self.reaction_times)
        super().save(*args, **kwargs)


class Leaderboard(TimeStampedModel):
    """
    Leaderboard entries for ranking players.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leaderboard_entries',
        verbose_name='Пользователь'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Очки'
    )
    rank = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Ранг'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=GameSession.DIFFICULTY_CHOICES,
        default='easy',
        verbose_name='Уровень сложности'
    )
    date_achieved = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата достижения'
    )
    avg_reaction_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Среднее время реакции (мс)'
    )

    class Meta:
        verbose_name = 'Запись в таблице лидеров'
        verbose_name_plural = 'Таблица лидеров'
        ordering = ['-score', 'date_achieved']
        unique_together = [['user', 'difficulty', 'date_achieved']]

    def __str__(self):
        return f'{self.user.username} - {self.score} очков ({self.difficulty})'

    def save(self, *args, **kwargs):
        # Auto-calculate rank based on score and difficulty
        if not self.rank:
            higher_scores = Leaderboard.objects.filter(
                difficulty=self.difficulty,
                score__gt=self.score
            ).count()
            self.rank = higher_scores + 1
        super().save(*args, **kwargs)


class Achievement(TimeStampedModel):
    """
    Achievements that users can earn.
    """
    ACHIEVEMENT_TYPES = [
        ('score', 'Очки'),
        ('reaction', 'Реакция'),
        ('games_played', 'Игр сыграно'),
        ('streak', 'Серия'),
        ('special', 'Особое'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    icon = models.ImageField(
        upload_to='achievements/',
        null=True,
        blank=True,
        verbose_name='Иконка'
    )
    achievement_type = models.CharField(
        max_length=20,
        choices=ACHIEVEMENT_TYPES,
        default='special',
        verbose_name='Тип достижения'
    )
    requirement = models.JSONField(
        default=dict,
        verbose_name='Требования',
        help_text='JSON объект с требованиями для получения достижения'
    )
    points = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Очки за достижение'
    )

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'

    def __str__(self):
        return self.name


class UserAchievement(TimeStampedModel):
    """
    Link between users and achievements they have earned.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name='Пользователь'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name='Достижение'
    )
    unlocked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Разблокировано'
    )

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
        unique_together = [['user', 'achievement']]
        ordering = ['-unlocked_at']

    def __str__(self):
        return f'{self.user.username} - {self.achievement.name}'


class Friendship(TimeStampedModel):
    """
    Friendship system - users can add each other as friends.
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendship_requests_sent',
        verbose_name='От пользователя'
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendship_requests_received',
        verbose_name='К пользователю'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Дружба'
        verbose_name_plural = 'Дружба'
        unique_together = [['from_user', 'to_user']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username} ({self.status})'


"""
Serializers for games app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    GameSession,
    Leaderboard,
    Achievement,
    UserAchievement,
    Friendship,
    Friendship,
    UserProfile
)
from django.db.models import Sum, Avg

User = get_user_model()


class GameSessionSerializer(serializers.ModelSerializer):
    """Serializer for game sessions."""
    user = serializers.StringRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = GameSession
        fields = (
            'id', 'user', 'username', 'game_state', 'score', 'difficulty',
            'time_played', 'is_completed', 'reaction_times', 'avg_reaction_time',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'avg_reaction_time')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for leaderboard entries."""
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Leaderboard
        fields = (
            'id', 'user_id', 'username', 'score', 'rank', 'difficulty',
            'date_achieved', 'avg_reaction_time', 'created_at'
        )
        read_only_fields = ('id', 'rank', 'date_achieved', 'created_at')


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements."""
    class Meta:
        model = Achievement
        fields = (
            'id', 'name', 'description', 'icon', 'achievement_type',
            'requirement', 'points', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer for user achievements."""
    achievement = AchievementSerializer(read_only=True)
    achievement_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = UserAchievement
        fields = ('id', 'achievement', 'achievement_id', 'unlocked_at', 'created_at')
        read_only_fields = ('id', 'unlocked_at', 'created_at')


class FriendshipSerializer(serializers.ModelSerializer):
    """Serializer for friendships."""
    from_username = serializers.CharField(source='from_user.username', read_only=True)
    to_username = serializers.CharField(source='to_user.username', read_only=True)
    friend_identifier = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Friendship
        fields = (
            'id', 'from_username', 'to_username',
            'status', 'created_at', 'updated_at', 'friend_identifier'
        )
        read_only_fields = ('id', 'from_username', 'to_username', 'status', 'created_at', 'updated_at')

    def validate(self, attrs):
        from_user = self.context['request'].user
        
        # Получаем friend_identifier из запроса
        friend_identifier = attrs.get('friend_identifier')
        if friend_identifier:
            # Ищем пользователя по username или email
            to_user = User.objects.filter(
                Q(username=friend_identifier) | Q(email=friend_identifier)
            ).first()
            
            if not to_user:
                raise serializers.ValidationError({
                    "friend_identifier": ["Пользователь не найден."]
                })
            
            # Проверяем, что пользователь не пытается добавить себя
            if from_user == to_user:
                raise serializers.ValidationError({
                    "friend_identifier": ["Нельзя добавить себя в друзья."]
                })
            
            # Проверяем, существует ли уже запрос на дружбу
            existing_friendship = Friendship.objects.filter(
                Q(from_user=from_user, to_user=to_user) | 
                Q(from_user=to_user, to_user=from_user)
            ).first()
            
            if existing_friendship:
                raise serializers.ValidationError({
                    "friend_identifier": ["Запрос на дружбу уже существует."]
                })
            
            # Устанавливаем найденного пользователя как to_user
            attrs['to_user'] = to_user
        else:
            raise serializers.ValidationError({
                "friend_identifier": ["Необходимо указать имя пользователя или email."]
            })
        
        return attrs

    def create(self, validated_data):
        # Удаляем friend_identifier из validated_data
        validated_data.pop('friend_identifier', None)
        # Автоматически устанавливаем from_user как текущего пользователя
        validated_data['from_user'] = self.context['request'].user
        # Статус всегда "pending" для новых запросов
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class FriendProfileSerializer(serializers.ModelSerializer):
    """Serializer for detailed friend profile."""
    username = serializers.CharField(source='user.username')
    avatar = serializers.ImageField(source='user.profile.avatar')
    bio = serializers.CharField(source='user.profile.bio')
    date_joined = serializers.DateTimeField(source='user.date_joined')
    
    # Stats
    games_played = serializers.SerializerMethodField()
    avg_reaction_time = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()
    high_scores = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'username', 'avatar', 'bio', 'date_joined',
            'games_played', 'avg_reaction_time', 'achievements', 'high_scores'
        )

    def get_games_played(self, obj):
        return GameSession.objects.filter(user=obj.user, is_completed=True).count()

    def get_avg_reaction_time(self, obj):
        sessions = GameSession.objects.filter(user=obj.user, is_completed=True).exclude(avg_reaction_time__isnull=True)
        if not sessions.exists():
            return None
        return sessions.aggregate(Avg('avg_reaction_time'))['avg_reaction_time__avg']

    def get_achievements(self, obj):
        user_achievements = UserAchievement.objects.filter(user=obj.user).select_related('achievement')
        return AchievementSerializer([ua.achievement for ua in user_achievements], many=True).data

    def get_high_scores(self, obj):
        # Top score for each difficulty
        scores = {}
        for diff in ['easy', 'medium', 'hard']:
            best = GameSession.objects.filter(
                user=obj.user, 
                difficulty=diff, 
                is_completed=True
            ).order_by('-score').first()
            if best:
                scores[diff] = best.score
        return scores


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for searching users."""
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'avatar')

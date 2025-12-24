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
    UserProfile
)

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

    class Meta:
        model = Friendship
        fields = (
            'id', 'from_user', 'from_username', 'to_user', 'to_username',
            'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        from_user = self.context['request'].user
        to_user = attrs.get('to_user')
        
        if from_user == to_user:
            raise serializers.ValidationError("Нельзя добавить себя в друзья.")
        
        # Check if friendship already exists
        if Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user
        ).exists() or Friendship.objects.filter(
            from_user=to_user,
            to_user=from_user
        ).exists():
            raise serializers.ValidationError("Запрос на дружбу уже существует.")
        
        return attrs

    def create(self, validated_data):
        validated_data['from_user'] = self.context['request'].user
        return super().create(validated_data)


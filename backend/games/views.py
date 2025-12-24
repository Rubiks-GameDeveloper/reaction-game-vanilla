"""
Views for games app - game sessions, leaderboard, achievements, friends.
"""
from rest_framework import generics, viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import (
    GameSession,
    Leaderboard,
    Achievement,
    UserAchievement,
    Friendship
)
from .serializers import (
    GameSessionSerializer,
    LeaderboardSerializer,
    AchievementSerializer,
    UserAchievementSerializer,
    FriendshipSerializer
)

User = get_user_model()


class GameSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for game sessions.
    Users can save and load their game sessions.
    """
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'is_completed']
    ordering_fields = ['score', 'created_at', 'time_played']
    ordering = ['-created_at']

    def get_queryset(self):
        return GameSession.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest game session for the current user."""
        latest_session = self.get_queryset().first()
        if latest_session:
            serializer = self.get_serializer(latest_session)
            return Response(serializer.data)
        return Response(
            {'message': 'Нет сохраненных игровых сессий.'},
            status=status.HTTP_404_NOT_FOUND
        )

    def perform_create(self, serializer):
        game_session = serializer.save()
        
        # Обновляем лидерборд только если игра завершена (is_completed=True)
        if game_session.is_completed:
            leaderboard_entry, created = Leaderboard.objects.get_or_create(
                user=game_session.user,
                difficulty=game_session.difficulty,
                defaults={
                    'score': game_session.score,
                    'avg_reaction_time': game_session.avg_reaction_time,
                }
            )
            
            if not created and game_session.score > leaderboard_entry.score:
                leaderboard_entry.score = game_session.score
                leaderboard_entry.avg_reaction_time = game_session.avg_reaction_time
                leaderboard_entry.date_achieved = game_session.created_at # Сохраняем дату нового рекорда
                leaderboard_entry.save()
        
        # Check for achievements
        self._check_achievements(game_session.user, game_session)
    
    def _check_achievements(self, user, game_session):
        """Check and award achievements based on game session."""
        achievements = Achievement.objects.all()
        for achievement in achievements:
            if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
                # Check if requirements are met
                requirement = achievement.requirement
                if self._meets_requirement(game_session, user, requirement):
                    UserAchievement.objects.create(user=user, achievement=achievement)

    def _meets_requirement(self, game_session, user, requirement):
        """Check if game session meets achievement requirement."""
        if not requirement:
            return False
        
        achievement_type = requirement.get('achievement_type')
        
        # Достижение: Высокий счет (1000+ очков)
        if achievement_type == 'high_score':
            return game_session.score >= requirement.get('min_score', 1000)
        
        # Достижение: Быстрая реакция (< 200мс)
        elif achievement_type == 'fast_reaction':
            if game_session.avg_reaction_time:
                return game_session.avg_reaction_time <= requirement.get('max_reaction_time', 200)
        
        # Достижение: Количество сыгранных игр (5+)
        elif achievement_type == 'games_played':
            user_games = GameSession.objects.filter(
                user=user, 
                is_completed=True
            ).count()
            return user_games >= requirement.get('min_games', 5)
        
        # Другие типы достижений
        if 'min_score' in requirement:
            return game_session.score >= requirement['min_score']
        if 'min_reaction_time' in requirement:
            if game_session.avg_reaction_time:
                return game_session.avg_reaction_time <= requirement['min_reaction_time']
        
        return False


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for leaderboard.
    Read-only, accessible to everyone.
    """
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['difficulty']
    ordering_fields = ['score', 'rank', 'date_achieved']
    ordering = ['-score']
    search_fields = ['user__username']

    @action(detail=False, methods=['get'])
    def top(self, request):
        """Get top N players (default 10)."""
        limit = int(request.query_params.get('limit', 10))
        difficulty = request.query_params.get('difficulty', None)
        
        queryset = self.get_queryset()
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        top_players = queryset[:limit]
        serializer = self.get_serializer(top_players, many=True)
        return Response(serializer.data)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for achievements.
    Read-only, accessible to everyone.
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['achievement_type']
    search_fields = ['name', 'description']


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user achievements.
    Users can view their own achievements.
    """
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user)


class FriendshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for friendship system.
    Users can send friend requests, accept/reject them, and view friends.
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a friend request."""
        friendship = self.get_object()
        if friendship.to_user != request.user:
            return Response(
                {'error': 'Вы не можете принять этот запрос.'},
                status=status.HTTP_403_FORBIDDEN
            )
        friendship.status = 'accepted'
        friendship.save()
        return Response({'message': 'Запрос на дружбу принят.'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a friend request."""
        friendship = self.get_object()
        if friendship.to_user != request.user:
            return Response(
                {'error': 'Вы не можете отклонить этот запрос.'},
                status=status.HTTP_403_FORBIDDEN
            )
        friendship.status = 'rejected'
        friendship.save()
        return Response({'message': 'Запрос на дружбу отклонен.'})

    @action(detail=False, methods=['get'])
    def friends(self, request):
        """Get list of accepted friends."""
        user = request.user
        friendships = Friendship.objects.filter(
            (Q(from_user=user) | Q(to_user=user)),
            status='accepted'
        )
        friends = []
        for friendship in friendships:
            friend = friendship.to_user if friendship.from_user == user else friendship.from_user
            friends.append({
                'id': friend.id,
                'username': friend.username,
                'profile': {
                    'avatar': friend.profile.avatar.url if friend.profile.avatar else None,
                    'bio': friend.profile.bio,
                }
            })
        return Response(friends)

    def _check_achievements(self, user, game_session):
        """Check and award achievements based on game session."""
        # This is a simplified version - you can expand it
        achievements = Achievement.objects.all()
        for achievement in achievements:
            if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
                # Check if requirements are met
                requirement = achievement.requirement
                if self._meets_requirement(game_session, user, requirement):
                    UserAchievement.objects.create(user=user, achievement=achievement)

    def _meets_requirement(self, game_session, user, requirement):
        """Check if game session meets achievement requirement."""
        # Simplified logic - expand based on your needs
        if 'min_score' in requirement:
            return game_session.score >= requirement['min_score']
        if 'min_reaction_time' in requirement:
            if game_session.avg_reaction_time:
                return game_session.avg_reaction_time <= requirement['min_reaction_time']
        return False


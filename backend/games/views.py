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
    FriendshipSerializer,
    FriendProfileSerializer,
    UserSearchSerializer
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
        print(f"Checking achievements for user {user.username}, total achievements: {achievements.count()}")
        for achievement in achievements:
            if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
                # Check if requirements are met
                requirement = achievement.requirement
                print(f"Checking achievement '{achievement.name}' with requirement: {requirement}")
                if self._meets_requirement(game_session, user, requirement):
                    UserAchievement.objects.create(user=user, achievement=achievement)
                    print(f"✓ Achievement '{achievement.name}' awarded to {user.username}!")
                else:
                    print(f"✗ Achievement '{achievement.name}' requirements not met")
            else:
                print(f"Achievement '{achievement.name}' already unlocked")

    def _meets_requirement(self, game_session, user, requirement):
        """Check if game session meets achievement requirement."""
        if not requirement:
            print("  No requirement specified")
            return False
        
        achievement_type = requirement.get('achievement_type')
        print(f"  Achievement type: {achievement_type}")
        
        # Достижение: Высокий счет
        if achievement_type == 'high_score' or 'min_score' in requirement:
            min_score = requirement.get('min_score', 500)
            result = game_session.score >= min_score
            print(f"  High score check: {game_session.score} >= {min_score} = {result}")
            return result
        
        # Достижение: Быстрая реакция
        elif achievement_type == 'fast_reaction' or 'max_reaction_time' in requirement:
            if game_session.avg_reaction_time:
                max_time = requirement.get('max_reaction_time', 500)
                result = game_session.avg_reaction_time <= max_time
                print(f"  Fast reaction check: {game_session.avg_reaction_time} <= {max_time} = {result}")
                return result
            print(f"  No avg_reaction_time data")
            return False
        
        # Достижение: Количество сыгранных игр
        elif achievement_type == 'games_played' or 'min_games' in requirement:
            user_games = GameSession.objects.filter(
                user=user, 
                is_completed=True
            ).count()
            min_games = requirement.get('min_games', 3)
            result = user_games >= min_games
            print(f"  Games played check: {user_games} >= {min_games} = {result}")
            return result
        
        print("  No matching achievement type")
        return False


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for leaderboard.
    Read-only, accessible to everyone.
    """
    queryset = Leaderboard.objects.select_related('user').all()
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
    ordering = ['-created_at']
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

    @action(detail=False, methods=['get'])
    def requests_received(self, request):
        """List pending incoming requests."""
        requests = Friendship.objects.filter(
            to_user=request.user,
            status='pending'
        )
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def requests_sent(self, request):
        """List pending outgoing requests."""
        requests = Friendship.objects.filter(
            from_user=request.user,
            status='pending'
        )
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def archive(self, request):
        """List rejected or archived requests."""
        user = request.user
        requests = Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            status='rejected'
        )
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search for users to add as friends."""
        query = request.query_params.get('q', '')
        if len(query) < 2:
             return Response([])
        
        user = request.user
        # Find users matching query (username or email)
        # Exclude self
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=user.id)
        
        # Exclude existing friends (accepted) or pending requests (sent by me)
        # We allow searching people who sent US a request (so we can accept via search if we want, or just see them)
        # But logic says: Don't show if already friends.
        
        existing_friend_ids = []
        friendships = Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            status='accepted'
        )
        for f in friendships:
            existing_friend_ids.append(f.to_user.id if f.from_user == user else f.from_user.id)
            
        pending_sent_to_ids = Friendship.objects.filter(
            from_user=user,
            status='pending'
        ).values_list('to_user_id', flat=True)

        users = users.exclude(id__in=existing_friend_ids).exclude(id__in=pending_sent_to_ids)
        
        serializer = UserSearchSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a sent friend request."""
        friendship = self.get_object()
        if friendship.from_user != request.user:
            return Response(
                {'error': 'Вы не можете отменить этот запрос.'},
                status=status.HTTP_403_FORBIDDEN
            )
        friendship.delete()
        return Response({'message': 'Запрос отменен.'})

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get friend's profile details."""
        # pk here is the FRIEND's USER ID, not the friendship ID
        friend_id = pk
        user = request.user
        
        # Allow viewing own profile without friend check
        if str(friend_id) != str(user.id):
            # Only check friendship if viewing someone else's profile
            is_friend = Friendship.objects.filter(
                (Q(from_user=user, to_user_id=friend_id) | Q(from_user_id=friend_id, to_user=user)),
                status='accepted'
            ).exists()

            if not is_friend:
                return Response(
                    {'error': 'Пользователь не является вашим другом.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get UserProfile
        try:
            profile = User.objects.get(id=friend_id).profile
        except:
             return Response(
                {'error': 'Профиль не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = FriendProfileSerializer(profile)
        return Response(serializer.data)


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


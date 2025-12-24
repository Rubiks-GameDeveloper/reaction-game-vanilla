"""
URLs for games app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GameSessionViewSet,
    LeaderboardViewSet,
    AchievementViewSet,
    UserAchievementViewSet,
    FriendshipViewSet
)

router = DefaultRouter()
router.register(r'sessions', GameSessionViewSet, basename='gamesession')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'user-achievements', UserAchievementViewSet, basename='userachievement')
router.register(r'friends', FriendshipViewSet, basename='friendship')

urlpatterns = [
    path('', include(router.urls)),
]


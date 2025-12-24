"""
Views for accounts app - authentication and user management.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserSerializer
)
from games.models import UserProfile

User = get_user_model()


# Добавьте документацию для API
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    create=extend_schema(
        summary="Регистрация пользователя",
        description="Создает нового пользователя и возвращает JWT токены",
        tags=['accounts']
    )
)
class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    Allows guest users to register.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Пользователь успешно зарегистрирован.'
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    create=extend_schema(
        summary="Вход в систему",
        description="Аутентифицирует пользователя и возвращает JWT токены",
        tags=['accounts']
    )
)
class LoginView(TokenObtainPairView):
    """
    User login endpoint.
    Returns JWT tokens on successful authentication.
    """
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile.
    Only authenticated users can access their own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class UserDetailView(generics.RetrieveAPIView):
    """
    Get public user information.
    Can be accessed by anyone (read-only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'


"""
Admin configuration for games app with XLSX export functionality.
"""
from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from .models import (
    GameSession,
    Leaderboard,
    Achievement,
    UserAchievement,
    Friendship,
    UserProfile
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""
    list_display = ('user', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    """Admin for GameSession with XLSX export."""
    list_display = ('user', 'score', 'difficulty', 'time_played', 'is_completed', 'created_at')
    list_filter = ('difficulty', 'is_completed', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'avg_reaction_time')
    date_hierarchy = 'created_at'
    actions = ['export_to_xlsx']

    def export_to_xlsx(self, request, queryset):
        """Export selected game sessions to XLSX file."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Game Sessions"

        # Headers
        headers = [
            'ID', 'Пользователь', 'Email', 'Очки', 'Сложность',
            'Время игры (сек)', 'Завершено', 'Среднее время реакции (мс)',
            'Дата создания', 'Дата обновления'
        ]
        ws.append(headers)

        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

        # Data rows
        for session in queryset:
            ws.append([
                session.id,
                session.user.username,
                session.user.email,
                session.score,
                session.get_difficulty_display(),
                session.time_played,
                'Да' if session.is_completed else 'Нет',
                round(session.avg_reaction_time, 2) if session.avg_reaction_time else '-',
                session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                session.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Create HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="game_sessions.xlsx"'
        wb.save(response)
        return response

    export_to_xlsx.short_description = "Экспортировать выбранные сессии в XLSX"

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    """Admin for Leaderboard."""
    list_display = ('user', 'score', 'rank', 'difficulty', 'date_achieved')
    list_filter = ('difficulty', 'date_achieved')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('rank', 'date_achieved', 'created_at', 'updated_at')
    ordering = ('-score',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin for Achievement."""
    list_display = ('name', 'achievement_type', 'points', 'created_at')
    list_filter = ('achievement_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """Admin for UserAchievement with manual assignment."""
    list_display = ('user', 'achievement', 'unlocked_at')
    list_filter = ('achievement', 'unlocked_at')
    search_fields = ('user__username', 'achievement__name')
    readonly_fields = ('unlocked_at', 'created_at', 'updated_at')
    actions = ['award_achievement']

    def award_achievement(self, request, queryset):
        """Manually award achievements to selected users."""
        # This action can be used to manually assign achievements
        pass

    award_achievement.short_description = "Назначить достижения вручную"


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    """Admin for Friendship."""
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
    readonly_fields = ('created_at', 'updated_at')


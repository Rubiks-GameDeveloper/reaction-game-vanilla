# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='achievements/', verbose_name='Иконка')),
                ('achievement_type', models.CharField(choices=[('score', 'Очки'), ('reaction', 'Реакция'), ('games_played', 'Игр сыграно'), ('streak', 'Серия'), ('special', 'Особое')], default='special', max_length=20, verbose_name='Тип достижения')),
                ('requirement', models.JSONField(default=dict, help_text='JSON объект с требованиями для получения достижения', verbose_name='Требования')),
                ('points', models.IntegerField(default=0, verbose_name='Очки за достижение')),
            ],
            options={
                'verbose_name': 'Достижение',
                'verbose_name_plural': 'Достижения',
            },
        ),
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('game_state', models.JSONField(default=dict, help_text='JSON объект с данными о состоянии игры', verbose_name='Состояние игры')),
                ('score', models.IntegerField(default=0, verbose_name='Очки')),
                ('difficulty', models.CharField(choices=[('easy', 'Легкий'), ('medium', 'Средний'), ('hard', 'Сложный')], default='easy', max_length=10, verbose_name='Уровень сложности')),
                ('time_played', models.IntegerField(default=0, verbose_name='Время игры (секунды)')),
                ('is_completed', models.BooleanField(default=False, verbose_name='Игра завершена')),
                ('reaction_times', models.JSONField(default=list, help_text='Список времен реакции в миллисекундах', verbose_name='Времена реакции')),
                ('avg_reaction_time', models.FloatField(blank=True, null=True, verbose_name='Среднее время реакции (мс)')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_sessions', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Игровая сессия',
                'verbose_name_plural': 'Игровые сессии',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Leaderboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('score', models.IntegerField(verbose_name='Очки')),
                ('rank', models.IntegerField(blank=True, null=True, verbose_name='Ранг')),
                ('difficulty', models.CharField(choices=[('easy', 'Легкий'), ('medium', 'Средний'), ('hard', 'Сложный')], default='easy', max_length=10, verbose_name='Уровень сложности')),
                ('date_achieved', models.DateTimeField(auto_now_add=True, verbose_name='Дата достижения')),
                ('avg_reaction_time', models.FloatField(blank=True, null=True, verbose_name='Среднее время реакции (мс)')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard_entries', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Запись в таблице лидеров',
                'verbose_name_plural': 'Таблица лидеров',
                'ordering': ['-score', 'date_achieved'],
                'unique_together': {('user', 'difficulty', 'date_achieved')},
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Аватар')),
                ('bio', models.TextField(blank=True, max_length=500, verbose_name='О себе')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль пользователя',
                'verbose_name_plural': 'Профили пользователей',
            },
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('unlocked_at', models.DateTimeField(auto_now_add=True, verbose_name='Разблокировано')),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_achievements', to='games.achievement', verbose_name='Достижение')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_achievements', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Достижение пользователя',
                'verbose_name_plural': 'Достижения пользователей',
                'ordering': ['-unlocked_at'],
                'unique_together': {('user', 'achievement')},
            },
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('status', models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('accepted', 'Принято'), ('rejected', 'Отклонено')], default='pending', max_length=10, verbose_name='Статус')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_requests_sent', to=settings.AUTH_USER_MODEL, verbose_name='От пользователя')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_requests_received', to=settings.AUTH_USER_MODEL, verbose_name='К пользователю')),
            ],
            options={
                'verbose_name': 'Дружба',
                'verbose_name_plural': 'Дружба',
                'ordering': ['-created_at'],
                'unique_together': {('from_user', 'to_user')},
            },
        ),
    ]


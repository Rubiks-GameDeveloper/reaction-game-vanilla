import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reaction_game.settings')
django.setup()

from games.models import Achievement

def seed_achievements():
    achievements = [
        {
            'name': 'Новичок',
            'description': 'Сыграйте 3 игры',
            'achievement_type': 'games_played',
            'requirement': {'min_games': 3},
            'points': 0
        },
        {
            'name': 'Снайпер',
            'description': 'Наберите 500 очков за одну игру',
            'achievement_type': 'high_score',
            'requirement': {'min_score': 500},
            'points': 0
        },
        {
            'name': 'Молниеносный',
            'description': 'Среднее время реакции до 500 мс',
            'achievement_type': 'fast_reaction',
            'requirement': {'max_reaction_time': 500},
            'points': 0
        }
    ]

    for data in achievements:
        achievement, created = Achievement.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"Достижение '{achievement.name}' создано.")
        else:
            # Обновляем существующие требования
            achievement.requirement = data['requirement']
            achievement.description = data['description']
            achievement.points = data['points']
            achievement.save()
            print(f"Достижение '{achievement.name}' обновлено.")

if __name__ == '__main__':
    seed_achievements()

from django.core.management.base import BaseCommand
from games.models import Achievement


class Command(BaseCommand):
    help = 'Create initial achievements'

    def handle(self, *args, **options):
        achievements_data = [
            {
                'name': 'Мастер скорострельщик',
                'description': 'Наберите 1000+ очков в одной игре',
                'achievement_type': 'score',
                'requirement': {'achievement_type': 'high_score', 'min_score': 1000},
                'points': 50,
            },
            {
                'name': 'Молниеносная реакция',
                'description': 'Среднее время реакции меньше 200мс',
                'achievement_type': 'reaction',
                'requirement': {'achievement_type': 'fast_reaction', 'max_reaction_time': 200},
                'points': 75,
            },
            {
                'name': 'Опытный игрок',
                'description': 'Сыграйте 5 завершенных игр',
                'achievement_type': 'games_played',
                'requirement': {'achievement_type': 'games_played', 'min_games': 5},
                'points': 25,
            }
        ]

        for achievement_data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создано достижение: "{achievement.name}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Достижение "{achievement.name}" уже существует')
                )

        self.stdout.write(
            self.style.SUCCESS('Все достижения созданы или уже существуют!')
        )

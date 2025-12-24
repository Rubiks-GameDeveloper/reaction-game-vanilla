"""
ASGI config for reaction_game project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reaction_game.settings')

application = get_asgi_application()


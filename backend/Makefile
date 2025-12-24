.PHONY: help migrate makemigrations runserver shell createsuperuser test

help:
	@echo "Доступные команды:"
	@echo "  make migrate          - Применить миграции"
	@echo "  make makemigrations    - Создать миграции"
	@echo "  make runserver         - Запустить сервер разработки"
	@echo "  make shell             - Открыть Django shell"
	@echo "  make createsuperuser   - Создать суперпользователя"
	@echo "  make test              - Запустить тесты"

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

runserver:
	python manage.py runserver

shell:
	python manage.py shell

createsuperuser:
	python manage.py createsuperuser

test:
	python manage.py test


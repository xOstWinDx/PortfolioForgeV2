install:
	pip install poetry
	poetry install --no-root

migrate:
	poetry run alembic upgrade head

run:
	make migrate
	poetry run hypercorn main:app --bind 0.0.0.0:8001 --workers $${WORKERS:-4}

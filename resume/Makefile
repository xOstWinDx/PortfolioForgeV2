install:
	pip install poetry
	poetry install --no-root

migrate:
	poetry run alembic upgrade head

run_app:
	make migrate
	poetry run hypercorn main:app --bind 0.0.0.0:8002 --workers $${WORKERS:-2}

run_consumer:
	make migrate
	poetry run python main.py --consumer
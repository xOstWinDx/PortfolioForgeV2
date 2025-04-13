install:
	pip install poetry
	poetry install --no-root --no-dev

run:
	poetry run hypercorn main:app --bind 0.0.0.0:8000 --workers $${WORKERS:-4}
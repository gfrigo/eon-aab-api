run:
	poetry run uvicorn src.main:app --reload

test:
	poetry run pytest

install:
	poetry install
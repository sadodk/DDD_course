# Domain-Driven Design in Python

This is the repository for the workshop Domain-Driven Design in Python.

## Prerequisites

- python 3.11+
- poetry 1.8.0+ (https://python-poetry.org)

## Development

first run `poetry install`

run `poetry run flask --app src/application/main.py run --debug`

### other tools

- Ruff is configured for formatting and checking errors: `poetry run ruff check .` and `poetry run ruff format .`
- Mypy is configured for type vailidations: `poetry run mypy src tests`

## Testing

run `poetry run pytest`

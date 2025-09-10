run-local:
	poetry run flask --app src/application/main.py run --debug --port 8080

mypy:
	poetry run mypy src tests

test:
	poetry run pytest

ngrok run:
	ngrok http 8080

test-main:
	poetry run pytest tests/application/test_main.py
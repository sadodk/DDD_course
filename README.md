# Domain-Driven Design in Python

This is the repository for the workshop Domain-Driven Design in Python

## Prerequisites

* python 3.11+
* poetry 1.8.0+ (https://python-poetry.org)

## Development

first run `poetry install`

run `poetry run flask --app src/application/main.py run --debug`

### other tools

* Ruff is configured for formatting and checking errors: `poetry run ruff check .` and `poetry run ruff format .`
* Mypy is configured for type vailidations: `poetry run mypy src tests`

## Testing

run `poetry run pytest`

## Running in github codespaces

If you use Github Codespaces, you don't need a tunneling tool. 
Instead, after executing poetry run flask (see above), make sure to go to the 
PORTS tab in your Github Codespaces instance (keyboard shortcut 'F1' -> 'Ports: 
Focus on Ports View') and change the visibility of port 5000 to Public. 

Afterwards, copy the Forwarded Address URL and [paste it in the workshop
interface](https://ddd-in-language.aardling.eu/setup#Set-client-endpoint-url).

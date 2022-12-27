run:
	docker-compose up -d -V

runb:
	docker-compose up -V

run-poetry:
	poetry install && poetry run bot

build:
	docker-compose build

exec:
	docker exec -it trading_view_connector bash

stop:
	docker-compose down -v --remove-orphans

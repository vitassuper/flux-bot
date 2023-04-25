run:
	docker-compose up -d -V

build:
	docker-compose build

exec:
	docker exec -it trading_view_connector bash

stop:
	docker-compose down -v --remove-orphans

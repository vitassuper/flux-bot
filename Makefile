%:
	@:
args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

run-dev:
	docker-compose -f docker-compose-dev.yml up -d
build-dev:
	docker-compose -f docker-compose-dev.yml build

run:
	docker-compose up -d
build:
	docker-compose build

stop:
	docker-compose down -v --remove-orphans

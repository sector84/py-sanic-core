.PHONY: all build start stop init_db tests reload logs

IMAGE=rest-api-mock:$(shell cat version.txt)

all: build start init_db

build:
	docker build -t $(IMAGE) .

start:
	docker-compose up -d

stop:
	docker-compose down

init_db:
	docker-compose exec app python3 /app/sys_scripts/run.py rest_api

tests:
	docker-compose exec app nosetests

reload:
	docker-compose exec app kill -HUP 1

logs:
	docker-compose logs -f --tail=50 app
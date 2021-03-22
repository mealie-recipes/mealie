setup:
	poetry install && \
	cd frontend && \
	npm install && \
	cd ..

backend: 
	poetry run python mealie/db/init_db.py && \
	poetry run python mealie/app.py

.PHONY: frontend
frontend:
	cd frontend && npm run serve

.PHONY: docs
docs:
	cd docs && poetry run python -m mkdocs serve

docker-dev:
	docker-compose -f docker-compose.dev.yml -p dev-mealie up --build

docker-prod:
	docker-compose -p mealie up --build -d

	
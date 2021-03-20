setup:
	poetry install && \
	cd frontend && \
	npm install && \
	cd ..

backend:
	source ./.venv/bin/activate && python mealie/app.py

vue:
	cd frontend && npm run serve

mdocs:
	source ./.venv/bin/activate && \
	cd docs && \
	mkdocs serve

docker-dev:
	docker-compose -f docker-compose.dev.yml -p dev-mealie up --build

docker-prod:
	docker-compose -p mealie up --build -d

	
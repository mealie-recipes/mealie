all: build backend
setup: setup-backend setup-frontend
build: setup build-frontend
backend: uvicorn
frontend: vue

setup-backend:
	poetry install

setup-frontend:
	cd frontend && npm install

build-frontend:
	cd frontend && npm run build

uvicorn:
	poetry run uvicorn mealie.app:app --host 0.0.0.0 --port 9000

mealie.app:
	poetry run python mealie/app.py

vue:
	cd frontend && npm run serve

mdocs:
	cd docs && poetry run mkdocs serve

docker-dev:
	docker-compose -f docker-compose.dev.yml -p dev-mealie up --build

docker-prod:
	docker-compose -p mealie up --build -d

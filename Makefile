.PHONY: help install test run down clean

help: ## Show available commands
	@echo "make            # show this help"
	@echo "make install    # install requirements locally"
	@echo "make test       # run tests"
	@echo "make run        # run API + Redis via Docker Compose"
	@echo "make down       # stop services"
	@echo "make clean      # remove containers/images"

install: ## Install requirements (detect tools)
	@python3 -V || { echo "Python3 not found. Install Python >=3.11"; exit 1; }
	@pip3 install --upgrade pip
	@pip3 install -e .
	@command -v docker >/dev/null 2>&1 || { echo "Docker not found. Install Docker: https://docs.docker.com/get-docker/"; }
	@command -v docker compose >/dev/null 2>&1 || command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose not found. Install: https://docs.docker.com/compose/"; }

run: ## Run API + Redis in Docker
	@docker compose up --build -d
	@echo "API on http://localhost:8000  (health: /healthz, chat: POST /chat)"

down: ## Stop services
	@docker compose down

clean: ## Teardown and removal
	@docker compose down -v --remove-orphans
	@docker system prune -f

test: ## Run tests
	@pytest -q

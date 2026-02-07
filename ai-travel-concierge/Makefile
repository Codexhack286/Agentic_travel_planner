.PHONY: help install test lint format clean run

help:
	@echo "AI Travel Concierge - Available Commands"
	@echo "========================================"
	@echo "install       - Install dependencies"
	@echo "test          - Run all tests"
	@echo "test-unit     - Run unit tests"
	@echo "test-int      - Run integration tests"
	@echo "lint          - Run linters"
	@echo "format        - Format code with black"
	@echo "clean         - Remove generated files"
	@echo "run           - Run the application"
	@echo "run-cli       - Run CLI mode"
	@echo "init-db       - Initialize vector database"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-int:
	pytest tests/integration/ -v

test-cov:
	pytest --cov=src --cov-report=html tests/

lint:
	flake8 src/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

run:
	python src/main.py

run-cli:
	python src/main.py --cli

init-db:
	python scripts/init_vectordb.py

dev:
	python src/main.py --reload

docker-build:
	docker build -t ai-travel-concierge .

docker-run:
	docker run -p 8000:8000 ai-travel-concierge

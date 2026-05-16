.PHONY: run run_docker test format lint clean

# Entorno local
run:
	streamlit run app.py

# Docker
run_docker:
	docker-compose up --build

# Testing
test:
	PYTHONPATH=. pytest tests/ -v

# Calidad de código
format:
	ruff format .
	ruff check . --fix

lint:
	ruff check .

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

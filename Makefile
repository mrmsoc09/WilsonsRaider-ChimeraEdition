.PHONY: setup build run lint test clean

setup:
python3 -m pip install --upgrade pip
pip install -r requirements.txt

build:
docker-compose build

run:
docker-compose up

lint:
flake8 orchestrator.py secret_manager.py hackerone_reporter.py tool_wrappers/ ai_agents/

test:
pytest

clean:
docker-compose down -v
rm -rf __pycache__ .pytest_cache

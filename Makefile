.PHONY: setup generate pipeline validate test lint clean

setup:
	python -m pip install -r requirements-dev.txt

generate:
	python -m src.generate_data

pipeline:
	python -m src.pipeline

validate:
	python -m src.verify_outputs

test:
	pytest

lint:
	ruff check .

clean:
	python -m src.clean_outputs


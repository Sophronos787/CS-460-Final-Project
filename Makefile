.PHONY: test run

test:
	pytest tests/ -v -s

run:
	python main.py "Serration" "Neural Sensors" "Orokin Cell" "Split Chamber"

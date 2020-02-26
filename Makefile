init:
	virtualenv -p /usr/bin/python3 venv

deps:
	pip3 install -r requirements.txt

dev-deps:
	pip3 install -r requirements-dev.txt

lint:
	pylint ekorre

test:
	pytest -v tests

install:
	python3 setup.py install

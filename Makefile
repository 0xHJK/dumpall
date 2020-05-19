dev:
	pip install setuptools wheel pytest black twine flake8

clean:
	rm -fr build dist .egg *.egg-info
	rm -fr .pytest_cache coverage.xml report.xml htmlcov
	find . | grep __pycache__ | xargs rm -fr
	find . | grep .pyc | xargs rm -f

uninstall:
	pip uninstall -y dumpall

install:
	python3 setup.py install

build:
	python3 setup.py sdist bdist_wheel

publish:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

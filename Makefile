clean:
	pip uninstall subdomain -y
	rm -fr build dist .egg *.egg-info
	find . | grep __pycache__ | xargs rm -fr
	find . | grep .pyc | xargs rm -f

install:
	python3 setup.py install

publish:
	pip3 install 'twine>=1.5.0'
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build .egg requests.egg-info

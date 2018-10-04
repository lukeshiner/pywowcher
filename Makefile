.PHONY: docs

init:
	pip install pipenv --upgrade
	pipenv lock -dr > requirements.txt
	pipenv sync

reinit:
	pipenv --rm
	make init

update_environment:
	pipenv --rm
	pipenv lock -dr  > requirements.txt
	pipenv sync --dev

test:
	pipenv run pytest

publish:
	pipenv run pip install 'twine>=1.5.0'
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/*
	rm -rf build dist .egg tabler.egg-info

publish-test:
	pipenv run pip install 'twine>=1.5.0'
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	rm -rf build dist .egg tabler.egg-info

docs:
	cd docs && pipenv run make html

lock:
	pipenv lock -dr > requirements.txt

coverage:
	pipenv run pytest --cov=pywowcher tests/
	pipenv run coverage html

PROJECT=cycless
all: README.md
	echo Hello.
test: test.py $(wildcard cycles/*.py)
	python test.py
test-deploy: build
	twine upload -r pypitest dist/*
test-install:
	pip install networkx numpy
	pip install --index-url https://test.pypi.org/simple/ $(PROJECT)


install: README.md
	./setup.py install
uninstall:
	-pip uninstall -y $(PROJECT)
build: README.md $(wildcard cycles/*.py)
	./setup.py sdist bdist_wheel


deploy: build
	twine upload dist/*
check:
	./setup.py check
pep8:
	autopep8 -r -a -a -i .
clean:
	-rm -rf build dist
distclean:
	-rm -rf build dist
	-rm -rf *.egg-info
	-rm .DS_Store
	find . -name __pycache__ | xargs rm -rf
	find . -name \*.pyc      | xargs rm -rf
	find . -name \*~         | xargs rm -rf

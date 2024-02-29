PKGNAME=cycless
all: README.md
	echo Hello.
test: test.py $(wildcard cycles/*.py)
	python test.py
FAU.gro:
	genice2 FAU > FAU.gro


%: temp_% replacer.py pyproject.toml
	python replacer.py < $< > $@

doc: README.md CITATION.cff 
	pdoc -o docs ./cycless --docformat google






test-deploy:
	poetry publish --build -r testpypi
test-install:
	pip install --index-url https://test.pypi.org/simple/ $(PKGNAME)
uninstall:
	-pip uninstall -y $(PKGNAME)
build: README.md $(wildcard cycles/*.py)
	poetry build
deploy:
	poetry publish --build
check:
	poetry check


clean:
	-rm -rf build dist
distclean:
	-rm -rf build dist
	-rm -rf *.egg-info
	-rm .DS_Store
	find . -name __pycache__ | xargs rm -rf
	find . -name \*.pyc      | xargs rm -rf
	find . -name \*~         | xargs rm -rf

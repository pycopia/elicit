# Makefile to simplify some common operations.

PYVER := 3.5
PYSUFFIX := m
PYTHON := $(shell python$(PYVER)$(PYSUFFIX)-config --prefix)/bin/python$(PYVER)

.PHONY: build install clean distclean develop test sdist requirements docs

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  build         to just build the packages."
	@echo "  install       to install from this workspace."
	@echo "  develop       to set up for local development."
	@echo "  test          to run unit tests."
	@echo "  clean         to clean up build artifacts."
	@echo "  distclean     to make source tree pristine."
	@echo "  sdist         to build source distribution."
	@echo "  publish       to push to PyPI."
	@echo "  docs          to build the documention."

build:
	$(PYTHON) setup.py build

install: build
	$(PYTHON) setup.py install --skip-build --optimize

requirements:
	pip$(PYVER) install -r dev-requirements.txt

develop: requirements
	$(PYTHON) setup.py develop --user

test:
	$(PYTHON) setup.py test

clean:
	$(PYTHON) setup.py clean
	find . -depth -type d -name __pycache__ -exec rm -rf {} \;

distclean: clean
	rm -rf costest.egg-info
	rm -rf dist
	rm -rf build
	make -C docs clean
	rm -rf .cache
	rm -rf .eggs

sdist: requirements
	$(PYTHON) setup.py sdist

publish:
	$(PYTHON) setup.py sdist upload
	$(PYTHON) setup.py bdist upload

docs:
	make -C docs html

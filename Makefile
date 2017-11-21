# Makefile to simplify some common operations.

# Find our exact Python 3 version.
PYTHONBIN ?= $(shell python3-config --prefix)/bin/python$(PYVER)$(ABIFLAGS)

PYVER := $(shell $(PYTHONBIN) -c 'import sys;print("{}.{}".format(sys.version_info[0], sys.version_info[1]))')
ABIFLAGS := $(shell $(PYTHONBIN)-config --abiflags)
SUFFIX := $(shell $(PYTHONBIN)-config --extension-suffix)


# Darwin using homebrew does not need sudo, but most other platforms do.
OSNAME = $(shell uname)
ifeq ($(OSNAME), Darwin)
	SUDO = 
else
	SUDO = sudo
endif

.PHONY: info build install clean distclean develop test sdist requirements docs

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  info          Show info about the Python being used."
	@echo "  build         to just build the packages."
	@echo "  install       to install from this workspace."
	@echo "  develop       to set up for local development."
	@echo "  test          to run unit tests."
	@echo "  clean         to clean up build artifacts."
	@echo "  distclean     to make source tree pristine."
	@echo "  sdist         to build source distribution."
	@echo "  publish       to push to PyPI."
	@echo "  docs          to build the documention."

info:
	@echo Found Python version: $(PYVER)$(ABIFLAGS)
	@echo Specific Python used: $(PYTHONBIN)
	@echo Python exension suffix: $(SUFFIX)
	@echo sudo: $(SUDO)

build:
	$(PYTHONBIN) setup.py build

install: build
	$(PYTHONBIN) setup.py install --skip-build --optimize

requirements:
	$(SUDO) pip$(PYVER) install -r dev-requirements.txt

develop: requirements
	$(PYTHONBIN) setup.py develop --user

test:
	$(PYTHONBIN) setup.py test

clean:
	$(PYTHONBIN) setup.py clean
	find . -depth -type d -name __pycache__ -exec rm -rf {} \;

distclean: clean
	rm -rf elicit.egg-info
	rm -rf dist
	rm -rf build
	make -C docs clean
	rm -rf .cache
	rm -rf .eggs

sdist: requirements
	$(PYTHONBIN) setup.py sdist

publish:
	$(PYTHONBIN) setup.py sdist upload
	$(PYTHONBIN) setup.py bdist_wheel upload

docs:
	make -C docs html

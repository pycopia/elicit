#!/usr/bin/env python

from setuptools import setup
from glob import glob

NAME = "elicit"


setup(name=NAME,
    packages = ["elicit"],
    install_requires = [],
    scripts = glob("bin/*"),
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    test_suite="tests",
    tests_require=['pytest'],

    description = "Library for making simple command interfaces.",
    long_description = """Library for making simple command interfaces with minimal dependencies.
    Includes an enhanced Python debugger.
    """,
    license = "Apache 2.0",
    author = "Keith Dart",
    author_email = "keith@dartworks.biz",
    url = "https://github.com/kdart/elicit",
    classifiers = ["Operating System :: POSIX",
                     "Topic :: Software Development :: Libraries :: Python Modules",
                     "Topic :: System :: Networking :: Monitoring",
                     "Intended Audience :: Developers"],
)

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

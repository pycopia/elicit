#!/usr/bin/env python

from setuptools import setup

NAME = "elicit"
VERSION = "0.1"


setup(name=NAME, version=VERSION,
      packages = ["elicit"],
      install_requires = [],
      #setup_requires=['setuptools_scm'],
      #use_scm_version=True,
      tests_require=['pytest'],

      description = "Library for making simple command interfaces.",
      long_description = """Library for making simple command interfaces with minimal dependencies.
      Includes an enhanced Python debugger.
      """,
      license = "Apache 2.0",
      author = "Keith Dart",
      author_email = "keith@dartworks.biz",
      url = "http://www.pycopia.net/",
      classifiers = ["Operating System :: POSIX",
                     "Topic :: Software Development :: Libraries :: Python Modules",
                     "Topic :: System :: Networking :: Monitoring",
                     "Intended Audience :: Developers"],
)

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

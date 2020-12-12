#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import codecs
import re

#Copied from wheel package
here = os.path.abspath(os.path.dirname(__file__))
#README = codecs.open(os.path.join(here, 'README.txt'), encoding='utf8').read()
#CHANGES = codecs.open(os.path.join(here, 'CHANGES.txt'), encoding='utf8').read()

with codecs.open(os.path.join(os.path.dirname(__file__), 'cycless', '__init__.py'),
                 encoding='utf8') as version_file:
    metadata = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", version_file.read()))

long_desc = "".join(open("README.md").readlines())

setup(name='cycless',
      python_requires='>=3.5',
      version=metadata['version'],
      description='A collection of algorithms for cycles in a graph.',
      long_description=long_desc,
      long_description_content_type="text/markdown",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        ],
      author='Masakazu Matsumoto',
      author_email='vitroid@gmail.com',
      url='https://github.com/vitroid/cycles/',
      keywords=['cycles', 'graph'],
      license='MIT',
      packages=find_packages(),
      install_requires=['networkx>=2', 'numpy',  'wheel'],
)

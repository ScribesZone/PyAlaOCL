# coding=utf-8
#
# inspired from http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
from __future__ import print_function
from setuptools import setup, find_packages
# from setuptools.command.test import test as TestCommand
import io
import os
import sys
import re

name = 'pyalaocl'

here = os.path.abspath(os.path.dirname(__file__))

def read(*file_names, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for file_name in file_names:
        with io.open(file_name, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst')


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name = name,
    version=find_version(name, '__init__.py'),
    author='megaplanet',
    author_email='megaplanet.github@megaplanet.org',
    license='',
    description='ala OCL expressions for Python, ' \
                'the UML Object Constraint Language',
    long_description=long_description,
    url='https://github.com/megaplanet/AlaOCL/',

    keywords = ['OCL','constraint','UML','validation','query language'],

    platforms='any',
    classifiers=[
        'Programming Language::Python:: 2.7',
        'Programming Language::Jython:: 2.7',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],


    #------ packages-----------------------------------------------------------
    #
    packages=[
        'pyalaocl',
        'pyalaocl.useocl',
        'pyalaocl.utils',
        'pyalaocl.modelio'],

    # install_requires=['Flask>=0.10.1',
    #                     'Flask-SQLAlchemy>=1.0',
    #                    'SQLAlchemy==0.8.2',
    #],
    # extras_require={
    #    'testing': ['pytest'],
    # }
    # include_package_data=True,


    #------ tests -------------------------------------------------------------
    test_suite='nose.collector'
)

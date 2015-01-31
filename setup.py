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

def read(file):
    encoding = 'utf-8'
    buf = []
    with io.open(file, encoding=encoding) as f:
            buf.append(f.read())
    return '\n'.join(buf)

def getLongDescription():
    return read('README.rst')

#-- get the version ------------------------------------------------
def getVersion():
    version_file = read(os.path.join(name, '__init__.py'))
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

#-- get the requirements from 'requirements.txt' ---------------
def getRequirements():
    from pip.req import parse_requirements
    install_requirements = parse_requirements('requirements.txt')
    requirements = [str(ir.req) for ir in install_requirements]
    return requirements

setup(
    name = name,
    version=getVersion(),
    author='megaplanet',
    author_email='megaplanet.github@megaplanet.org',
    license='',
    description='ala OCL expressions for Python, ' \
                'the UML Object Constraint Language',
    long_description=getLongDescription(),
    url='https://github.com/megaplanet/PyAlaOCL/',
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

    install_requires=getRequirements(),
    # extras_require={
    #    'testing': ['pytest'],
    # }
    # include_package_data=True,


    #------ tests -------------------------------------------------------------
    test_suite='nose.collector'
)

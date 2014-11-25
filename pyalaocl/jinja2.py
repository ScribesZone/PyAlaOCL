# coding=utf-8

import pyalaocl
from pyalaocl import *

__all__ = (
    'addOCLToEnvironment',
)
_FILTERS = {
    'asSet': asSet,
    'asBag': asBag,
    'asSeq': asSeq,
    #
    # ... could be extended ...
    #
}

_GLOBALS = {
    'floor': floor,
    'isUndefined': isUndefined,
    'oclIsUndefined': oclIsUndefined,
    'oclIsKindOf': oclIsKindOf,
    'oclIsTypeOf': oclIsTypeOf,
    'isCollection': isCollection,
    'asSet': asSet,
    'asBag': asBag,
    'asSeq': emptyCollection
    #
    # ... could be extended ...
    #
}


def addOCLToEnvironment(jinja2Environment):
    """
    Add OCL functions to a jinja2 environment so that OCL can be
    used in jinja2 templates.

    :param jinja2Environment: Jinja2 environment to be instrumented.
    :type jinja2Environment: jinja2.Environment
    :return: The modified environment.
    :rtype: jinja2.Environment
    """
    jinja2Environment.filters.update(_FILTERS)
    jinja2Environment.globals.update(_GLOBALS)


try:
    # noinspection PyUnresolvedReferences
    from org.modelio.api.modelio import Modelio

    WITH_MODELIO = True
except:
    WITH_MODELIO = False

if WITH_MODELIO:
    import pyalaocl.symbols
    globalSymbols = pyalaocl.symbols.SymbolManager.symbols(kind='scope')
    _GLOBALS.update(globalSymbols)

# coding=utf-8

import pyalaocl

__all__ = (
    'addOCLToEnvironment',
)
_FILTERS = {
    'asSet': pyalaocl.asSet,
    'asBag': pyalaocl.asBag,
    'asSeq': pyalaocl.asSeq,
    #
    # ... could be extended ...
    #
}

_GLOBALS = {
    'floor': pyalaocl.floor,
    'isUndefined': pyalaocl.isUndefined,
    'oclIsUndefined': pyalaocl.oclIsUndefined,
    'oclIsKindOf': pyalaocl.oclIsKindOf,
    'oclIsTypeOf': pyalaocl.oclIsTypeOf,
    'isCollection': pyalaocl.isCollection,
    'asSet': pyalaocl.asSet,
    'asBag': pyalaocl.asBag,
    'asSeq': pyalaocl.emptyCollection
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
    import pyalaocl.utils.symbols
    globalSymbols = pyalaocl.utils.symbols.SymbolManager.symbols(kind='scope')
    _GLOBALS.update(globalSymbols)

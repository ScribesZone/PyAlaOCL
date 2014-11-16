# coding=utf-8

from pyalaocl import *

#__all__ = (
#    'addOCLtoEnvironment',
#)
_FILTERS = {
    'asSet': asSet,
    'asBag': asBag,
    'asSeq': asSeq,
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
}

try:
    # noinspection PyUnresolvedReferences
    from org.modelio.api.modelio import Modelio

    WITH_MODELIO = True
except:
    WITH_MODELIO = False

if WITH_MODELIO:

    # TODO: in fact, this piece of code should be in 'modelio' module
    # and it should be possible to import global stuff at once
    # - at the top level script
    # - as jinja global
    # - in any python module
    # Lambda expressions cannot be defined directly in the loop. See below:
    # http://stackoverflow.com/questions/841555/
    # whats-going-on-with-the-lambda-expression-in-this-python-function?rq=1
    def _newIsInstanceFun(metaInterface):
        return lambda e: isinstance(e, metaInterface)

    from pyalaocl.modelio import MetaInterface
    for m_interface in MetaInterface.allInstances():
        raise NotImplemented  # FIXME
        metaName = m_interface.metaName
        _GLOBALS[metaName] = m_interface

        isFunction = _newIsInstanceFun(m_interface)
        _GLOBALS['is' + metaName] = isFunction
        globals()['is' + metaName] = isFunction

def addOCLtoEnvironment(jinja2Environment):
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



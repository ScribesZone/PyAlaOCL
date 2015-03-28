# coding=utf-8

from abc import ABCMeta, abstractmethod
import sys
from collections import Counter
import keyword
import __builtin__
import re


def isBuiltin(name):
    return name in __builtin__.__dict__


def isValidNewIdentifier(name,
                         allowRedefinition=False,
                         object=None,
                         scope=None,
                         existingIdentifiers=None,
):
    return (
        re.match("[_A-Za-z][_a-zA-Z0-9]*$", name)
        and (not keyword.iskeyword(name))
        and (not isBuiltin(name))
        and (
            allowRedefinition or
            ( ( existingIdentifiers is None or name not in existingIdentifiers)
              and (object is None or not hasattr(object, name))
              and (scope is None or (name not in scope))
            )
        )
    )


def startUpper(name):
    if name == '':
        return name
    return name[0].upper() + name[1:]

def startLower(name):
    if name == '':
        return name
    return name[0].lower() + name[1:]


class SymbolManager(object):
    __symbolChanges = []

    @classmethod
    def symbolChanges(cls, kind=None, group=None, module=None, target=None):
        return [
            change for change in cls.__symbolChanges
            if ((kind is None or change.kind==kind)
                and (group is None or change.group==group)
                and (module is None or change.module==module)
                and (target is None or change.target==target ))
        ]

    @classmethod
    def count(cls, attribute):
        count = Counter()
        for change in cls.symbolChanges():
            count[getattr(change,attribute)] += 1
        return count

    @classmethod
    def symbols(cls, kind=None, group=None, module=None, target=None):
        changes = \
            cls.symbolChanges(
                kind=kind, group=group, module=module, target=target)
        return dict({ (change.symbol, change.valueAfter)
                      for change in changes })

    @classmethod
    def undo(cls, kind=None, group=None, module=None, target=None):
        changes = \
            cls.symbolChanges(
                kind=kind, group=group, module=module, target=target)
        for change in changes:
            change.undo()

    @classmethod
    def _addSymbolChange(cls, change):
        cls.__symbolChanges.append(change)

    @classmethod
    def _removeSymbolChange(cls, change):
        if change in cls.symbolChanges:
            cls.__symbolChanges.remove(change)



class SymbolChange(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, kind, group,
                 target, symbol, value):
        self.group = group
        self.kind = kind
        self.module = None
        self.target = target
        self.symbol = symbol
        self.wasDefined = None
        self.valueBefore = None
        self.valueAfter = value
        SymbolManager._addSymbolChange(self)

    @abstractmethod
    def undo(self):
        SymbolManager._removeSymbolChange(self)
        # do undo



class ScopeSymbolChange(SymbolChange):
    def __init__(self, group, scope, symbol, value):
        super(ScopeSymbolChange, self).__init__(
            'scope', group, scope, symbol, value)
        if symbol in scope:
            self.wasDefined = True
            self.valueBefore = scope[symbol]
        else:
            self.wasDefined = False
            self.valueBefore = None
        scope[symbol] = value
        if '__name__' in scope and scope['__name__'] in sys.modules:
            self.module = sys.modules[scope['__name__']]

    def undo(self):
        if self.wasDefined:
            self.target[self.symbol] = self.valueBefore
        else:
            del self.target[self.symbol]
        super(ScopeSymbolChange,self).undo()



class ObjectSymbolChange(SymbolChange):
    def __init__(self, group, object_, symbol, value):
        super(ObjectSymbolChange, self).__init__(
            'object', group, object_, symbol, value)
        if hasattr(object_, symbol):
            self.wasDefined = True
            self.valueBefore = getattr(object_, symbol)
        else:
            self.wasDefined = False
            self.valueBefore = None
        setattr(object_, symbol, value)
        if hasattr(object_,'__module__',) and object_.__module__ \
                in sys.modules:
            self.module = sys.modules[object_.__module__]

    def undo(self):
        if self.wasDefined:
            setattr(self.target, self.symbol, self.valueBefore)
        else:
            delattr(self.target, self.symbol)
        super(ObjectSymbolChange, self).undo()


def unload():
    SymbolManager.undo()

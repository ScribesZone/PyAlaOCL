# coding=utf-8

__all__ = (
    'addSuperclass',
    'superclassOf',
    'attributeOf',
    'readOnlyPropertyOf',
    'methodOf',
    'classMethodOf',
    'staticMethodOf',
    'isValidNewIdentifier',
    'export',
)


import types
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


#==============================================================================
#   Functions and decorators to instrument existing classes
#==============================================================================


def addSuperclass(superclassOrSuperclasses, subclassOrSubclasses):
    """
    Add a (list of) superclasses to a(list of) subclass(es) and this after
    the fact.

    See the @superclassOf decorator for more information. This version is
    more general as it can take various superclasses and it can be used both
    after the definition of subclasses but also superclasses.

    :param superclassOrSuperclasses: A class or a list of classes to be
    added as superclass(es) to the subclasses.

    :type superclassOrSuperclasses: objectclass|tuple[objeclass]|list[
    objectclass]

    :param subclassOrSubclasses: A class or a list of classes to be
    instrumented.

    :type subclassOrSubclasses: type|tuple[type]|list[type]
    :return: Nothing
    :rtype: NoneType
    """

    # print superclassOrSuperclasses,type(superclassOrSuperclasses)
    if isinstance(superclassOrSuperclasses,
                  (types.TypeType ,types.ClassType)):
        superclasses = (superclassOrSuperclasses,)
    else:
        superclasses = tuple(superclassOrSuperclasses)

    if isinstance(subclassOrSubclasses,(types.TypeType,types.ClassType)):
        subclasses = [subclassOrSubclasses]
    else:
        subclasses = list(subclassOrSubclasses)
    for subclass in subclasses:
        if object in subclass.__bases__:
            others = list(subclass.__bases__)
            others.remove(object)
            bases = tuple(others) + superclasses + (object,)
        else:
            bases = list(subclass.__bases__)
            for superclass in superclasses:
                if superclass not in bases:
                    bases.append(superclass)
        subclass.__bases__ = tuple(bases)


def superclassOf(subclassOrSubclasses):
    """
    Class decorator allowing to add *after the fact* a super class to one
    or various classes given as parameter.

    This decorator is useful to add behavior to existing libraries or classes
    that cannot be modified. Python builtin classes cannot be modified.
    In the context of jython it works well, but only on direct concrete class.
    That is, java implement and inheritance graph is not followed.
    :param subclassOrSubclasses: the class or the list of class to add the
    superclass to. That is this (these) class(es) become subclasses of the
    superclass decorated. See the examples provided below.
    :param subclassOrSubclasses: class|tuple[class]|list[class]

    This decorator must be applied to a class that do *not* inherits from
    'object'. In this case just use old class style for the inheritance root.

    Example
    -------

    In the example below two classes *Kangaroo* and *ColoredKangaroo* are
    assumed to be defined in a (weired) library. For some reasons their
    source codes cannot modified. We want however to add *Animal* as a
    superclass of *Kangaroo* and *ColoredAnimal* as a superclass of
    *ColoredKangaroo* .

    First let's start with the existing library:

        >>> class Kangaroo(object):
        ...     def who(self):
        ...         return "kangaroo"
        >>> class ColoredKangaroo(Kangaroo):
        ...     def __init__(self,color):
        ...         self.color = color
        ...     def who(self):
        ...         return self.color+" "+super(ColoredKangaroo,self).who()

    This library being defined somewhere, the *Animal* (old-style) class
    is added after the fact to the existing class; here to *Kangaroo* because
    this is the root class in the library.

        >>> @superclassOf(Kangaroo)
        ... #noinspection PyClassicStyleClass
        ... class Animal:                       # not class Animal(object)
        ...     def who(self):
        ...         return "animal"
        ...     def babies(self):
        ...         return "babies are %ss" % self.who()

    Then a superclass is defined for all colored animals. Here we have only
    one subclass to instrument be we still use [ ] to show that the decorator
    accept a list of classes to be instrumented.

        >>> @superclassOf([ColoredKangaroo])
        ... class ColoredAnimal(Animal):
        ...     def getColor(self):
        ...         return self.color

    Now it is time to play with animals and kangaroos.

        >>> k = Kangaroo()
        >>> print k.who()
        kangaroo

    Using the method *babies* added in the *Animal* superclass shows that
    polymorphism work properly. Otherwise it would say that babies are
    "animals".

        >>> print k.babies()
        babies are kangaroos

    Now we can check that subclasses work properly as well.

        >>> bk = ColoredKangaroo("blue")
        >>> print bk.who()
        blue kangaroo
        >>> print bk.babies()
        babies are blue kangaroos

    In particular is is important to check what happen when a superclass has
    been added to a subclass. This is the case for *ColoredAnimal* and the
    method *getColor*.

        >>> print bk.color
        blue
        >>> print bk.getColor()
        blue
    """

    def decorate(superclass):
        # if isinstance(subclassOrSubclasses,type):
        #     subclasses = [subclassOrSubclasses]
        # else:
        #     subclasses = list(subclassOrSubclasses)
        # for subclass in subclasses:
        #     if object in subclass.__bases__:
        #         subclass.__bases__ = (superclass,object)
        #     else:
        #         subclass.__bases__ = subclass.__bases__ + (superclass,)
        addSuperclass(superclass,subclassOrSubclasses)
        return superclass

    return decorate


def attributeOf(object, name, value, objectName=None):
    if isValidNewIdentifier(name, object=object, allowRedefinition=True):
        try:
            setattr(object, name, value)
            return True
        except AttributeError as e:
            if objectName is None:
                if hasattr(object, name):
                    objectName = object.name
                else:
                    objectName = 'some(%s)' % type(object)
            print 'attributeOf: Error instrumenting %s.%s' \
                  % (objectName, name)
            print 'attributeOf: %s' % e
            return False

def readOnlyPropertyOf(class_,propertyName=None):
    def decorate(function):
        name = function.__name__ if propertyName is None else propertyName
        setattr(class_, name, property(function))
        return None
    return decorate


def methodOf(class_, methodName=None):
    def decorate(function):
        name = function.__name__ if methodName is None else methodName
        setattr(class_, name, function)
        return None
    return decorate


def classMethodOf(class_, methodName=None):
    def decorate(function):
        name = function.__name__ if methodName is None else methodName
        setattr(class_, name, classmethod(function))
        return None
    return decorate


def staticMethodOf(class_, methodName=None):
    def decorate(function):
        name = function.__name__ if methodName is None else methodName
        setattr(class_, name, staticMethodOf(function))
        return None
    return decorate


def export(scope, name, value,
           existingIdentifiers=None, allowRedefinition=False):
    if isValidNewIdentifier(name,
                            allowRedefinition=allowRedefinition,
                            scope=scope,
                            existingIdentifiers=existingIdentifiers,
                            ):
        if name in scope:
            if scope[name] is not value:
                print 'pyalaocl.modelio.injector: allowed redefinition of %s.'\
                    'It was of type %s.' \
                    % (name,type(scope[name]))
        scope[name] = value
        if '__all__' in scope:
            if isinstance(scope['__all__'], tuple):
                scope['__all__'] = list(scope['__all__'])
            scope['__all__'].append(name)
    else:
        if name in scope:
            if scope[name] is not value:
                pass
                #print 'Notice: "%s" symbol was in scope. Not redefined. ' \
                #    'It remains a %s' % (name,type(scope[name]))
        else:
            print 'Notice: "%s" symbol will not be available at toplevel'\
                  % name


# execute tests if launched from command line
if __name__ == "__main__":
    import doctest
    doctest.testmod()

# coding=utf-8

__all__ = (
    'addSuperclass',
    'superclassof',
)


import types

#==============================================================================
#   Functions and decorators to instrument existing classes
#==============================================================================


def addSuperclass(superclassOrSuperclasses, subclassOrSubclasses):
    """
    Add a (list of) superclasses to a(list of) subclass(es) and this after
    the fact.

    See the @superclassof decorator for more information. This version is
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
            subclass.__bases__ = tuple(others) + superclasses + (object,)
        else:
            subclass.__bases__ = subclass.__bases__ + superclasses
            # print "    = %s " % str(subclass.__bases__)


def superclassof(subclassOrSubclasses):
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

        >>> @superclassof(Kangaroo)
        ... #noinspection PyClassicStyleClass
        ... class Animal:                       # not class Animal(object)
        ...     def who(self):
        ...         return "animal"
        ...     def babies(self):
        ...         return "babies are %ss" % self.who()

    Then a superclass is defined for all colored animals. Here we have only
    one subclass to instrument be we still use [ ] to show that the decorator
    accept a list of classes to be instrumented.

        >>> @superclassof([ColoredKangaroo])
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


# execute tests if launched from command line
if __name__ == "__main__":
    import doctest

    doctest.testmod()

# coding=utf-8

# This module does not export any symbol. Importing it inject methods into
# Java Collections but no new symbol is defined at the global level.
__all__ = (
)

import pyalaocl
from pyalaocl import Set, Bag, Seq, Invalid
from pyalaocl.injector import addSuperclass


#==============================================================================
#   Functions and decorators to instrument existing classes
#==============================================================================

# noinspection PyUnresolvedReferences
from java.util import Collections
# noinspection PyUnresolvedReferences
import java.util


# noinspection PyClassicStyleClass
class JavaCollectionExtension(pyalaocl.GenericCollection):
    # Defined in java
    # size()  java native
    # __len__ jython
    #        empty
    # isEmpty()  java native
    # __contains__ jython
    # contains
    # containsAll

    def count(self,element):
        """
            >>> java.util.ArrayList([1,1,2,4,1]).count(1)
            3
            >>> java.util.ArrayList([1,1,2,4,1]).count(17)
            0
            >>> java.util.HashSet([1,1,2,4,1]).count(17)
            0
            >>> java.util.HashSet([1,1,2,4,1]).count(1)
            1
        """
        return java.util.Collections.frequency(self,element)

    def includes(self,value):
        """
            >>> java.util.ArrayList([1,2]).includes(2)
            True
            >>> java.util.ArrayList([1,2]).includes(8)
            False
        """
        return self.contains(value)

    def excludes(self,value):
        return not self.contains(value)

    def includesAll(self,anyCollection):
        """
        """
        return self.containsAll(anyCollection)

    def including(self,value):
        return self.asCollection().including(value)

    def excluding(self,value):
        return self.asCollection().excluding(value)

    def union(self,anyCollection):
        return self.asCollection().union(anyCollection)

    def intersection(self,anyCollection):
        return self.asCollection().intersection(anyCollection)

    def __and__(self,anyCollection):
        return self.intersection(anyCollection)

    # abstract method
    def hasDuplicates(self):
        raise NotImplementedError()

    # abstract method
    def duplicates(self):
        raise NotImplementedError()

    def flatten(self):
        return self.asCollection().flatten()

    def select(self,expression):
        return self.asCollection().select(expression)

    def collectNested(self,expression):
        return self.asCollection().collectNested(expression)

    def sortedBy(self,expression):
        return self.asCollection().sortedBy(expression)

    def asSet(self):
        return Set.new(self)

    def asBag(self):
        return Bag.new(self)

    def asSeq(self):
        return Seq.new(self)

    # abstract method
    def asCollection(self):
        raise NotImplementedError()

    # abstract method
    def emptyCollection(self):
        raise NotImplementedError()




# noinspection PyClassicStyleClass
class JavaSetExtension(JavaCollectionExtension):

    def difference(self,anyCollection):
        return self.asSet().difference(anyCollection)

    def __sub__(self,anyCollection):
        return self.difference(anyCollection)

    def symmetricDifference(self,anyCollection):
        return self.asSet().symmetricDifference(anyCollection)

    def hasDuplicates(self):
        return False

    def duplicates(self):
        return Bag.new()

    def asCollection(self):
        return Set.new(self)

    def emptyCollection(self):
        return Set.new()


# noinspection PyClassicStyleClass
class JavaListExtension(JavaCollectionExtension):

    def hasDuplicates(self):
        return Bag.new(self).hasDuplicates()

    def duplicates(self):
        return Bag.new(self).duplicates()

    def asCollection(self):
        return Seq.new(self)

    def emptyCollection(self):
        return Seq.new()

    def append(self,value):
        return Seq.new(self+[value])

    def prepend(self,value):
        return Seq.new([value]+self)

    def subSequence(self,lower,upper):
        try:
            return Seq.new(list(self)[lower - 1:upper])
        except:
            raise Invalid(".subSequence(%s,%s) failed: No such element."%(lower,upper))
    def at(self,index):
        try:
            return self.get(index-1)
        except:
            raise Invalid(".at(%s) failed: No such element." % index)

    def first(self):
        try:
            return self.get(0)
        except:
            raise Invalid(".at(%s) failed: No such element.")

    def last(self):
        try:
            return self.get(self.size()-1)
        except:
            raise Invalid(".at(%s) failed: No such element.")




# noinspection PyUnresolvedReferences
import java.util
# noinspection PyUnresolvedReferences
import java.lang

# noinspection PyUnresolvedReferences
# from java.util import List as Java
# noinspection PyUnresolvedReferences
# from java.util import Set
# noinspection PyUnresolvedReferences
# from java.lang import Iterable

JavaJDKConversionRules = (
    (java.util.Set,Set),
    (java.util.List,Seq),
    (java.lang.Iterable,Seq)
)
pyalaocl.CONVERTER.registerConversionRules('java',JavaJDKConversionRules)

JAVA_JDK_LISTS = [
    java.util.ArrayList,
    java.util.Vector,
    java.util.LinkedList,
]

JAVA_JDK_SETS = [
    java.util.EnumSet,
    java.util.HashSet,
    java.util.TreeSet,
]

JAVA_JDK_COLLECTIONS = JAVA_JDK_SETS + JAVA_JDK_LISTS

addSuperclass(JavaSetExtension,JAVA_JDK_SETS)
addSuperclass(JavaListExtension,JAVA_JDK_LISTS)




# execute tests if launched from command line
if __name__ == "__main__":
    import doctest

    doctest.testmod()

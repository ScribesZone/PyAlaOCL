# -*- coding: utf-8 -*-
"""
Collection of classes and functions to ease the translation of OCL expressions
into python.

.. moduleauthor:: jeanmariefavre

* =   -> ==
* x.isUndefined() -> isUndefined(x)
* x.isUndefined() -> isUndefined(x)

Number
------
* x.abs() -> abs(x)
* x.min(y) -> min(x,y)
* x.max(y) -> max(x,y)

Integer
-------
* div   /
* mod   %

Real
----
* x.floor() ->   floor(x)
* x.round() ->   round(x)

String
------
* s1.size()             -> len(s1)
* s1.contact(s2)        -> s1+s2
* s1.substring(i1,i2)   -> s1[i1,i2]   TODO: check
* s1.toUpper()          -> s1.upper()
* s1.toLower()          -> s1.lower()

Boolean
-------
* true                  -> True
* false                 -> False
* xor                   -> TODO: implement it as xor(a,b)  or  a \|xor| b with
                            Infix
* implies               -> TODO: like xor
* if c then a else b    -> a if c else b

Enumeration
-----------
* E::x                  -> E.x

Collection
----------
* coll                  C(coll)
* coll->op(...)         C(coll).op(...)

* Set{ ... }            -> Set( ... )
* Bag{ ... }            -> Bag( ... )
* OrderedSet{ ... }     -> OrderedSet( ... )
* Sequence{ ... }       -> Seq( ... )
* Sequence {1..5, 10..20} -> Seq{range(1,5)+range(10,20)}

UML based features
------------------
* oclIsNew              -> Not available. Can be use only with post condition
* oclAsType             -> Not necessary thanks for dynamic typing in python.




from org.modelio.vcore.smkernel import SmList
def select(self,f): return [x for x in self if f(x) ]
a = selectedElements[0].getOwnedAttribute()
print type(a),type(a[0])
print select(a,lambda x:x.isModifiable())
SmList.select = select
print a.select(Attribute.isModifiable)

"""


__all__ = (
    'floor',

    'isUndefined',
    'oclIsUndefined',
    'Invalid',
    'oclIsKindOf',
    'oclIsTypeOf',

    'Collection',
    'Set',
    'Bag',
    'Seq',
    'asSet',
    'asBag',
    'asSeq',

    'isCollection',
    'asCollection',
    'emptyCollection',

    'listAll',
)




from abc import ABCMeta,abstractmethod


def floor(r):
    """ Return the largest integer which is not greater than the parameter.
    """
    import math
    return math.floor(r)


def isUndefined(value):
    """
    Indicates if the given parameter is undefined (None) or not.
    :param value: any kind of value.
    :type value: any
    :return: True if the value is None.
    :rtype: bool

    Examples:
        >>> print isUndefined(3)
        False
        >>> print isUndefined(None)
        True
    """
    try:
        return value is None
    except:
        return True  # see OCL 11.3.4


def oclIsUndefined(value):
    return isUndefined(value)


class Invalid(Exception):
    def __init__(self,msg):
        super(Invalid,self).__init__(msg)


def oclIsKindOf(value,aType):
    """
    Evaluates to True if the type of the value is *exactly* the type given as
    a second parameter is an instance of type or one of its subtypes directly
    or indirectly. Use the method oclIsTypeOf if you want to check if a value
    is exactly of a given type.


    :param value: A scalar value, a collection or an object.
    :type value; Any
    :param aType: The type to check the value against
                  (e.g. int, float, str, unicode, bool or a class)
    :type aType: type
    :return: True if value is compatible with the type aType.
    :rtype: bool
    Examples:
        >>> print oclIsKindOf(3,int)
        True
        >>> print oclIsKindOf("3",int)
        False
        >>> print oclIsKindOf(2.5,float)
        True
        >>> print oclIsKindOf("hello",basestring)
        True
        >>> print oclIsKindOf(True,bool)
        True
        >>> class Person(object): pass
        >>> print oclIsKindOf(Person(),Person)
        True
        >>> print oclIsKindOf(Person(),object)
        True
        >>>
    """
    return isinstance(value,aType)


def oclIsTypeOf(value,aType):
    """
    Return True if the type of the value is *exactly* the type given as a
    second parameter. This function does not take into account sub-typing
    relationships. If this is what is intended, use oclIsKindOf instead.

    :param value: A scalar value, a collection or an object.
    :type value; Any
    :param aType: The type to check the value against
                  (e.g. int, float, str, unicode, bool or a class)
    :type aType: type
    :return: True if value is compatible with the type aType.
    :rtype: bool
    Examples:
        >>> print oclIsTypeOf("hello",str)
        True
        >>> print oclIsTypeOf("hello",basestring)
        False
        >>> print oclIsTypeOf(u"çüabè",unicode)
        True
    """
    return type(value) == aType


def evaluate(value,expression):
    """
    Evaluate an expression on a given value
    :param value:
    :type value:
    :param expression:
    :type expression:
    :return:
    :rtype:
    Examples:
        >>> evaluate(1,lambda x:x*2)
        2
        >>> evaluate('hello',len)
        5
        >>> evaluate('hello',str.islower)
        True
        >>> evaluate('hello','islower')
        True
        >>> evaluate('hello','len(_)')
        5
        >>> evaluate('hello','_.islower()')
        True
        >>> class A(object):
        ...    a = 3
        ...    def __init__(self):
        ...        self.b = 10
        ...    def c(self):
        ...        return 25
        >>> evaluate(A(),'a')
        3
        >>> evaluate(A(),'b')
        10
        >>> evaluate(A(),'c')
        25

    """
    if callable(expression):
        return expression(value)
    elif isinstance(expression,(str,unicode)):
        try:
            r = getattr(value,expression)
        except AttributeError:
            if '_' in expression:
                _ = value
                return eval(expression)
            else:
                msg = "evaluate(): %s is not an attribute of the type %s" \
                    % expression,type(value)
                raise Invalid(msg)
        if callable(r):
            return r()
        else:
            return r

def evaluatePredicate(value,predicate):
    r = evaluate(value,predicate)
    t = type(r)
    if t is not bool:
        msg = "Predicate expected. Returned a value of type" \
              " %s instead of a boolean" % t
        raise Invalid(msg)
    else:
        return r


def flatten(value):
    """
    Return an OCL collection with all the elements at the first level.

    :param value: The collection to be flatten
    :rtype value: iterable[iterable]
    :return: A flatten collection.
    :rtype: Seq
    """
    try:
        return value.flatten()
    except NameError:
        # print "-----flatten(%s)"%value
        if isCollection(value):
            #print "  collection"
            flat = []
            for e in value:
                flat.extend(flatten(e))
            # print "    -> %s" %flat
            return flat
        else:
            return [value]

#==============================================================================
#                              Collections
#==============================================================================





# noinspection PyClassicStyleClass
class GenericCollection:
    """
    Class used both to define brand new OCL collection (classes under
    Collection) but also to define JavaCollectionExtension. Due to restriction
    of class instrumentation we use old-style class, hence object is not the
    base class.
    """
    def __init__(self):
        pass

    def __len__(self):
        """
        Return the size of the collection.

        Not in OCL but  pythonic.
        :return: The number of elements in the collection
        :rtype: int

        Examples:
            >>> len(Set(2,2,3))
            2
            >>> len(Bag(1,1,1))
            3
            >>> len(Set(Set()))
            1
        """
        return self.size()

    def isEmpty(self):
        return self.size() == 0

    def notEmpty(self):
        return not self.isEmpty()

    def includes(self,value):
        """
        Return True if the value is in the collection.
        :param value: Any kind of value.
        :type value: any
        :return: True if the element is in set, False otherwise.
        :rtype: bool
        Examples:
            >>> Set(1,3,"a").includes("3")
            False
            >>> Set(1,3,"a").includes(3)
            True
            >>> Set(Set()).includes(Set())
            True
            >>> Set().includes(Set())
            False
            >>> 3 in Set(2,3,1)
            True
            >>> "hello" in Set("a","b")
            False

            >>> Bag(10,"a",3,3,10,10).includes(10)
            True
            >>> Bag(2).includes(5)
            False
            >>> 2 in Bag(2,2)
            True

            >>> Seq(10,2,2,3).includes(3)
            True
            >>> 2 in Seq(1,0,1)
            False

        """
        return value in self

    def excludes(self,value):
        return value not in self

    def includesAll(self,elements):
        for e in elements:
            if e not in self:
                return False
        return True

    def excludesAll(self,elements):
        for e in elements:
            if e in self:
                return False
        return True

    def __or__(self,anyCollection):
        return self.union(anyCollection)


    def any(self,predicate):
        """
        Return any element in the collection that satisfy the predicate.

        This operation is non deterministic as various elements may satisfy
        the predicate.
        If not element satisfies the predicate an exception is raised.
        See OCL-11.9.1
        :param predicate: A predicate, that is a function returning a boolean.
        :type predicate: X->bool
        :return: Any element satisfying the predicate.
        :rtype X:

        Examples:
            >>> Set(1,2,-5,-10).any(lambda x:x<0) in [-5,-10]
            True
            >>> Set(1,2).any(lambda x:x<0)
            Traceback (most recent call last):
              ...
            Invalid: .any(...) failed: No such element.
        """
        # noinspection PyTypeChecker
        for e in self:
            if evaluatePredicate(e,predicate):
                return e
        raise Invalid(".any(...) failed: No such element.")


    def max(self):
        return max(self)

    def min(self):
        return min(self)

    def sum(self):
        """
        Sum of the number in the collection.
        Examples:
            >>> Set(1,0.5,-5).sum()
            -3.5
            >>> Set().sum()
            0
        """
        return sum(self)

    def selectByKind(self,aType):
        return self.select(lambda e:oclIsKindOf(e,aType))

    def selectByType(self,aType):
        return self.select(lambda e:oclIsTypeOf(e,aType))

    def reject(self,predicate):
        """
        Discard from the set all elements that satisfy the predicate.

        :param predicate: A predicate, that is a function returning a boolean.
        :return: The set without the rejected elements.
        :rtype set:

        Examples:
            >>> Set(2,3,2.5,-5).reject(lambda e:e>2) == Set(2,-5)
            True
            >>> Set(Set(1,2,3,4),Set()).reject(lambda e:e.size()>3) \
                     == Set(Set())
            True
        """
        return self.select(lambda e:not evaluatePredicate(e,predicate))

    def collect(self,expression):
        return self.collectNested(expression).flatten()

    def __getattr__(self,name):
        """

        :param name:
        :return:

        Examples:
            >>> class P(object):
            ...      def __init__(self,x):
            ...         self.a = x
            >>> P1 = P(1)
            >>> P4 = P(4)
            >>> P1.a
            1
            >>> P4.a
            4
            >>> Set(P1,P4).a == Bag(1,4)
            True
        """
        return self.collect(lambda e:getattr(e,name))

    def forAll(self,predicate):
        """
        Return True if the predicate given as parameter is satisfied by all
        elements of the collection.

        :param predicate: A predicate, that is a function returning a boolean.
        :type predicate: X->bool
        :return: Whether or not the predicate is satisfied by all elements.
        :rtype bool:

        Examples:
            >>> Set(2,3,5,-5).forAll(lambda e:e>=0)
            False
            >>> Set(2,3,5).forAll(lambda e:e>=0)
            True
            >>> Set().forAll(lambda e:e>=0)
            True
            >>> Bag(4,4,4).forAll(lambda e:e==4)
            True
            >>> Seq(Bag(1),Set(2),Seq(3)).forAll(lambda e:e.size()==1)
            True
        """
        # noinspection PyTypeChecker
        for e in self:
            if not evaluatePredicate(e,predicate):
                return False
        return True

    def exists(self,predicate):
        """
        Return True if the predicate given as parameter is satisfied by at
        least one element of the collection.

        :param predicate: A predicate, that is a function returning a boolean.
        :type predicate: X->bool
        :return: Whether or not the predicate is satisfied by at least one
                element.
        :rtype bool:

        Examples:
            >>> Set(2,3,5,-5).exists(lambda e:e<0)
            True
            >>> Set(2,3,5).exists(lambda e:e<0)
            False
            >>> Set().exists(lambda e:e>=0)
            False
            >>> Bag(Set(),Set(),Set(2),Set(3)).exists(lambda e:e.size()==1)
            True
        """
        # noinspection PyTypeChecker
        for e in self:
            if evaluatePredicate(e,predicate):
                return True
        return False

    def one(self,predicate):
        """
        Return True if the predicate given as parameter is satisfied by at
        one and only one element in the collection.

        :param predicate: A predicate, that is a function returning a boolean.
        :type predicate: X->bool
        :return: Whether or not the predicate is satisfied by exactly one
                element.
        :rtype bool:

        Examples:
            >>> Set(2,3,5,-5).one(lambda e:e<0)
            True
            >>> Bag(2,3,5,-5,-5).one(lambda e:e<0)
            False
            >>> Set().one(lambda e:e>=0)
            False
            >>> Seq().one(lambda e:e>=0)
            False
            >>> Seq(1).one(lambda e:e>=0)
            True
            >>> Bag(Set(2),Set(),Set(3),Set()).one(lambda e:e.size()==0)
            False
        """
        foundOne = False
        # noinspection PyTypeChecker
        for e in self:
            found = evaluatePredicate(e,predicate)
            if found and foundOne:
                return False
            elif found:
                foundOne = True
        return foundOne

    def closure(self,expression):
        """
        Return the transitive closure of the expression for all element in
        the collection.

        See OCL (section 7.6.5.


        :param expression: The expression to be applied again and again.
        :type: X->X
        :return: A set representing the transitive closure including the
        source elements/
        :type: Seq[X]
        Examples:

            >>> def f(x):
            ...     successors = {1:[2], 2:[1, 2, 3], 3:[4], 4:[], \
                                  5:[5], 6:[5], 7:[5, 7]}
            ...     return successors[x]
            >>> Set(1).closure(f) == Seq(1,2,3,4)
            True
            >>> Set(5).closure(f) == Seq(5)
            True
            >>> Seq(6,6,3).closure(f) == Seq(6,3,5,4)
            True
        """

        # FIXME: returns always a sequence, but the type changes in OCL.
        from collections import deque
        sources = list(self)
        to_visit = deque(sources)
        visited = []
        while len(to_visit) != 0:
            current = to_visit.popleft()
            if current not in visited:
                result = evaluate(current,expression)
                if isCollection(result):
                    successors = listAll(result)
                else:
                    successors = [result]
                # print "visited %s -> %s" % (current,successors)
                for s in successors:
                    if s not in visited:
                        to_visit.append(s)
                visited.append(current)
        return Seq.new(visited)

    def iterate(self):
        # FIXME: Not implemented (See 7.6.6)
        raise NotImplementedError()

    def isUnique(self,expression):
        return not self.collect(expression).hasDuplicates()




from collections import deque

class Collection(object,GenericCollection):
    """
    Base class for OCL collections.
    Collections are either:
    * sets (Set),
    * ordered set (OrderedSet)
    * bags (Bag),
    * sequences (Seq)
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def size(self):
        pass

    @abstractmethod
    def count(self,element):
        pass

    @abstractmethod
    def including(self,value):
        pass

    @abstractmethod
    def excluding(self,value):
        pass

    @abstractmethod
    def union(self,value):
        pass

    @abstractmethod
    def select(self,expression):
        pass

    @abstractmethod
    def flatten(self):
        pass

    @abstractmethod
    def collectNested(self,expression):
        pass

    @abstractmethod
    def hasDuplicates(self):
        pass

    @abstractmethod
    def duplicates(self):
        pass

    @abstractmethod
    def sortedBy(self,expression):
        pass

    def asCollection(self):
        return self

    @abstractmethod
    def emptyCollection(self):
        return self

    @abstractmethod
    def asSet(self):
        pass

    @abstractmethod
    def asBag(self):
        pass

    @abstractmethod
    def asSeq(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def __eq__(self,value):
        pass

    def __ne__(self,value):
        return not self.__eq__(value)

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __contains__(self,item):
        pass

    @abstractmethod
    def __iter__(self):
        pass




#------------------------------------------------------------------------------
#   OCL Sets
#------------------------------------------------------------------------------


def asSet(collection):
    """
    Convert the given collection to a Set
    :param collection:
    :return:
    :rtype: Set
    """
    try:
        return collection.asSet()
    except AttributeError:
        return Set.new(collection)


class Set(Collection):
    """
    Set of elements.

    This class mimics OCL Sets. Being a set, there are no duplicates and no
    ordering of elements. By contrast to OCL Sets, here a set can contain
    any kind of elements at the same time. OCL sets are homogeneous,
    all elements being of the same type (or at least same supertype).
    """

    def __init__(self,*args):
        """
        Create a set from some elements.

        Eliminate duplicates if any.
        Examples:
           >>> Set(10,"a",3,10,10) == Set(10,"a",3)
           True
           >>> Set() <> Set(10,"a",3)
           True
           >>> Set(10,10).size()
           1
           >>> Set(Set()).size()
           1
           >>> Set("hello").size()
           1
           >>> Set(Set(2),Set(2)).size()
           1
        """
        # We cannot have Counter here. So list is ok (see listAll)
        super(Set,self).__init__()
        self.theSet = set(list(args))

    @classmethod
    def new(cls,anyCollection=()):
        newSet = cls()
        newSet.theSet = set(anyCollection)
        return newSet

    def emptyCollection(self):
        return Set.new()

    def size(self):
        """
        Return the size of the set.
        :return: The size of the set.
        :rtype: int
        Examples:
            >>> Set(1,4,2,1,1).size()
            3
            >>> Set().size()
            0
        """
        return len(self.theSet)

    def isEmpty(self):
        return True if self.theSet else False

    def count(self,value):
        """
        Return the number of occurrence of the value in the set (0 or 1).
        :param value: The element to search in the set.
        :type value: any
        :return: 1 if the element is in the set, 0 otherwise.
        :rtype: bool
        Examples:
            >>> Set(1,3,"a").count("3")
            0
            >>> Set(1,3,3,3).count(3)
            1
        """
        return 1 if value in self.theSet else 0

    def includes(self,value):
        return value in self.theSet

    def including(self,value):
        """
        Add the element to the set if not already there.
        :param value: The element to add to the set.
        :type value: any
        :return: A set including this element.
        :rtype: Set
        Examples:
            >>> Set(1,3,"a").including("3") == Set(1,"3",3,"a")
            True
            >>> Set(1,3,3,3).including(3) == Set(3,1)
            True
        """
        fresh = set(self.theSet)
        fresh.add(value)
        return Set.new(fresh)

    def excluding(self,value):
        """
        Excludes a value from the set (if there).
        :param value: The element to add to the set.
        :type value: any
        :return: A set including this element.
        :rtype: Set
        Examples:
            >>> Set(1,3,"a").excluding("3") == Set(1,3,"a")
            True
            >>> Set(1,3,3,3).excluding(3) == Set(1)
            True
        """
        fresh = set(self.theSet)
        fresh.discard(value)
        return Set.new(fresh)

    def union(self,anyCollection):
        """
        Add all elements from the collection given to the set.
        :param anyCollection: A collection of values to be added to this set.
        :type anyCollection: collection
        :return: A set including all values added plus previous set elements.
        :rtype: Set
        Examples:
            >>> Set(1,3,'a').union([2,3,2]) == Set(1,3,"a",2)
            True
            >>> Set(1,3,3,3).union(Set(2,1,8)) == Set(1,2,3,8)
            True
            >>> Set().union(Set()) == Set()
            True
            >>> Set(1,3) | [2,3] == Set(1,2,3)
            True
        """
        assert isCollection(anyCollection), \
            'Any collection expected, but found %s' % anyCollection
        # We don't need to take special care with Counter as we remove
        # duplicates
        fresh = set(self.theSet)
        fresh = fresh | set(anyCollection)
        return Set.new(fresh)

    def __or__(self,anyCollection):
        return self.union(anyCollection)

    def intersection(self,anyCollection):
        """
        Retain only elements in the intersection between this set and the
        given collection.

        :param anyCollection: A collection of values to be added to this set.
        :type anyCollection: collection
        :return: A set including all values added plus previous set elements.
        :rtype: Set
        Examples:
            >>> Set(1,3,"a").intersection(["a","a",8]) == Set("a")
            True
            >>> Set(1,3,3,3).intersection(Set(1,3)) == Set(1,3)
            True
            >>> Set(2).intersection(Set()) == Set()
            True
            >>> Set(2) & Set(3,2) == Set(2)
            True
        """

        assert isCollection(anyCollection), \
            'Any collection expected, but found %s' % anyCollection
        # Don't need to take special care with Counter as we remove duplicates
        fresh = set(self.theSet)
        fresh = fresh & set(anyCollection)
        return Set.new(fresh)

    def __and__(self,anyCollection):
        return self.intersection(anyCollection)

    def difference(self,anyCollection):
        """
        Remove from the set all values in the collection.
        :param anyCollection: Any collection of values to be discarded from
                this set.
        :type anyCollection: collection
        :return: This set without the values in the collection.
        :rtype: Set
        Examples:

            >>> Set(1,3,"a").difference([2,3,2,'z']) == Set(1,"a")
            True
            >>> Set(1,3,3,3).difference(Set(1,3)) == Set()
            True
            >>> Set().difference(Set()) == Set()
            True
            >>> Set(1,3) - [2,3] == Set(1)
            True
        """
        assert isCollection(anyCollection), \
            'Any collection expected, but found %s' % anyCollection
        fresh = set(self.theSet)
        # No need for take special care with Counter as we remove duplicates
        fresh = fresh - set(anyCollection)
        return Set.new(fresh)

    def __sub__(self,anyCollection):
        return self.difference(anyCollection)

    def symmetricDifference(self,anyCollection):
        """
        Return the elements that are either in one set but not both sets.

        In fact this method accept any collection, but it is first converted
        to a set.

        :param anyCollection: A collection to make the difference with.
        :type anyCollection: collection
        :return: The symmetric difference.
        :rtype: Set
        Examples:
            >>> Set(1,2).symmetricDifference(Set(3,2)) == Set(1,3)
            True
            >>> Set(Set()).symmetricDifference(Set()) == Set(Set())
            True
        """
        assert isCollection(anyCollection), \
            'Any collection expected, but found %s' % anyCollection
        fresh = set(self.theSet)
        other_set = set(anyCollection)
        fresh = (fresh | other_set) - (fresh & other_set)
        return Set.new(fresh)

    def hasDuplicates(self):
        """
        Return always False for sets.

        This method is an extension to OCL. It makes is defined on sets just
        for consistency but is more useful for Bags or Sequences.
        :return: True
        :rtype: bool
        """
        return False

    def duplicates(self):
        """ Return always an empty bag for a set """
        return Bag.new()

    def flatten(self):
        """
        If the set is a set of collections, then return the set-union of all
        its elements.

        :return: Set
        :rtype: Set
        Examples:
            # >>> Set(Set(2)).flatten() == Set(2)
            # True
            # >>> Set(Set(Set(2)),Set(2)).flatten() == Set(2)
            # True
            >>> Set(Set(2,3),Set(4),Set(),Bag("a"),Bag(2,2)).flatten() \
                   == Set(2,3,4,"a")
            True

            #>>> Set().flatten() == Set()
            # True
            # >>> Set(2,3).flatten() == Set(2,3)
            # True
            # >>> Set(2,Set(3),Set(Set(2))).flatten() == Set(2,3)
            # True
        """

        fresh = set()
        for e in self.theSet:
            if isCollection(e):
                flat_set = set(flatten(e))
            else:
                flat_set = {e}
            fresh = fresh | flat_set
        return Set.new(fresh)

    def select(self,predicate):
        """
        Retain in the set only the elements satisfying the expression.

        :param predicate: A predicate, that is a function returning a boolean.
        :return: The set with only the selected elements.
        :rtype Set:

        Examples:
            >>> Set(2,3,2.5,-5).select(lambda e:e>2) == Set(3,2.5)
            True
            >>> Set(Set(1,2,3,4),Set()).select(lambda e:e.size()>3) \
                    == Set(Set(1,2,3,4))
            True
        """
        return Set.new(set([e for e in self if evaluatePredicate(e,predicate)]))

    def collectNested(self,expression):
        """
        Return a bag of values resulting from the evaluation of the given expression
        on all elements of the set.

        The transformation from this set to a bag is due to the fact that
        the expression can generate duplicates.

        :param expression: A function returning any kind of value.
        :type expression: X -> Y
        :return: The bag of values produced.
        :rtype Bag[Y]:

        Examples:
            >>> Set(2,3,5,-5).collectNested(lambda e:e*e) == Bag(25,25,4,9)
            True
            >>> Set(2,3).collectNested(lambda e:Bag(e,e)) \
                    == Bag(Bag(2,2),Bag(3,3))
            True
        """
        return Bag.new(map((lambda e:evaluate(e,expression)),self.theSet))

    def sortedBy(self,expression):
        # FIXME: should return a OrderedSet
        return \
            Seq.new(sorted(self.theSet,key=(lambda e:evaluate(e,expression))))

    def asSet(self):
        return self

    def asBag(self):
        return asBag(self.theSet)

    def asSeq(self):
        return asSeq(self.theSet)

    def __str__(self):
        """
        Return a string representation of the set where elements are
        separated by ", ".

        The result is non deterministic as there is no ordering between
        elements.

        :return: A string.
        :rtype: str

        Examples:
            >>> str(Set())
            'Set()'
            >>> str(Set(3))
            'Set(3)'
            >>> str(Set(3,2)).startswith('Set(')
            True
        """
        body = ", ".join(map(str,self.theSet))
        return "Set(%s)" % body

    def __repr__(self):
        return self.__str__()

    def __eq__(self,value):
        """
        Return true if the value given is a Set and has exactly the same
        elements.

        :param value: Any value, but succeed only for sets.
        :type value: any
        :return: True if "value" is a set with the same elements.
        :rtype: bool

        Examples:
            >>> Set() == []
            False
            >>> Set() == Set()
            True
            >>> Set(2,3,3) == Set(3,2)
            True
            >>> Set(2,"3",4) == Set(2,4,3)
            False
            >>> Set("hello") == Set("hello")
            True
            >>> Set(Set(1)) == Set(Set(1))
            True
            >>> Set(Set(1),Set(2,1)) == Set(Set(1,2),Set(1))
            True
        """
        if not isinstance(value,Set):
            return False
        return self.theSet == value.theSet

    def __ne__(self,value):
        return not self.__eq__(value)

    def __hash__(self):
        return hash(frozenset(self.theSet))

    def __iter__(self):
        """ Make Sets iterable for pythonic usage.
        :return: the iterator for this Set
        """
        return self.theSet.__iter__()

    def __contains__(self,item):
        return item in self.theSet




#------------------------------------------------------------------------------
#   OCL Bags
#------------------------------------------------------------------------------


def asBag(anyCollection):
    """
    :param anyCollection:
    :return:
    """
    try:
        return anyCollection.asBag()
    except AttributeError:
        return Bag.new(anyCollection)


from collections import Counter

class Bag(Collection):

    def __init__(self,*args):
        """
        Create a bag from some elements.

        Examples:
           >>> Bag(10,"a",3,10,10) == Bag(10,10,"a",3,10)
           True
           >>> Bag(2) <> Bag(2,2,2)
           True
           >>> Bag(3,3,4) == Bag(3,4,3)
           True
           >>> Bag(2,3) == Bag(3,2)
           True
           >>> Bag(Set(2,3),Set(3,2)).size()
           2
        """
        super(Bag,self).__init__()
        # We cannot have Counter here. So list is ok (see listAll)
        self.theCounter = Counter(list(args))

    @classmethod
    def new(cls,anyCollection=()):
        newBag = Bag()
        if isinstance(anyCollection,Counter):
            newBag.theCounter = anyCollection.copy()
            # Remove the 0 and negative elements from the counter. This
            # weird trick is indicated in python documentation for Counter.
            newBag.theCounter += Counter()
        elif isinstance(anyCollection,Bag):
            newBag.theCounter = anyCollection.theBag.copy()
        else:
            newBag.theCounter = Counter(listAll(anyCollection))
        return newBag

    def emptyCollection(self):
        return Bag.new()

    def size(self):
        """
        Return the total number of elements in the bag.
        :rtype! int
        Examples:
           >>> Bag(10,"a",3,3,10,10).size()
           6
           >>> Bag(2).size()
           1
           >>> Bag().size()
           0
        """
        return sum(self.theCounter.values())

    def count(self,value):
        """
        Return the number of occurrences of a given value within the bag.

        Examples:
           >>> Bag(10,"a",3,3,10,10).count(10)
           3
           >>> Bag(2).count(5)
           0
           >>> Bag().count(2)
           0
           >>> Bag(Set(1),Set(1)).count(Set(1))
           2
        """
        return self.theCounter[value]

#    def __getitem__(self,key):
#        return self.theCounter[key]

    def including(self,value):
        """
        Add a value into the bag.

        :param value: The value to be added.
        :type: any
        :return: The bag with one more occurrence of the value.
        :rtype: Bag

        Examples:
            >>> Bag(10,10,2,10).including(10) == Bag(10,10,10,10,2)
            True
            >>> Bag(10,10,2,10).including("a") == Bag(10,10,10,2,'a')
            True
            >>> Bag().including(34) == Bag(34)
            True
        """
        fresh = self.theCounter.copy()
        fresh[value] += 1
        return Bag.new(fresh)

    def excluding(self,value):
        """
        Remove *all* elements corresponding to the given value from the bag.

        :param value: Any value within the bag or not.
        :type: any
        :return: The bag without any occurrence of 'value'.
        :rtype: Bag

        Examples:
            >>> Bag(10,10,2,10).excluding(10) == Bag(2)
            True
            >>> Bag(10,10,2,10).excluding("a") == Bag(10,10,10,2)
            True
            >>> Bag().excluding(34) == Bag()
            True
        """
        fresh = self.theCounter.copy()
        del fresh[value]
        return Bag.new(fresh)

    def union(self,anyCollection):
        """
        Add to the bag all values in the collection given as a parameter.

        Examples:
           >>> Bag(10,"a",3,3,10,10).union(Bag(10,10,"b")) \
                    == Bag("b","a",3,3,10,10,10,10,10)
           True
           >>> Bag(2,4).union([2,4]) == Bag(2,2,4,4)
           True
           >>> Bag().union([1]) == Bag(1)
           True
           >>> Bag(3,3) | Set(3,3,3,2) == Bag(3,3,3,2)
           True
           >>> Bag(2,3,1) | Bag(3,3,2,4) == Bag(3,3,3,2,2,1,4)
           True
           >>> Bag(2,3,1) | Counter([3,3,2,4]) == Bag(3,3,3,2,2,1,4)
           True

        """
        assert isCollection(anyCollection), \
            'Any collection expected, but found %s' % anyCollection
        fresh = self.theCounter.copy()
        fresh.update(listAll(anyCollection))
        return Bag.new(fresh)

    def intersection(self,anyCollection):
        """
        Retain only elements that are in common with the given collection.

        Examples:
            >>> Bag(10,"a",3,3,10,10).intersection(Bag(10,10,"b")) == Bag(10,10)
            True
            >>> Bag(2,4).intersection(Bag(2,4)) == Bag(2,4)
            True
            >>> Bag() & [1] == Bag()
            True
            >>> Bag(3,3) & Set(3,3,3,2) == Bag(3)
            True
        """
        assert isCollection(anyCollection), \
            'Any collection expected, but found %s' % anyCollection
        return Bag.new(self.theCounter & Counter(list(anyCollection)))

    def __and__(self,anyCollection):
        return self.intersection(anyCollection)


    def sum(self):
        """
        Return the sum of all elements in a bag including duplicates.

        :return: the sum of all elements .
        :rtype: int

        Examples:
            >>> Bag().sum()
            0
            >>> Bag(3,3,2,3).sum()
            11
        """
        return sum([e * n for (e,n) in self.theCounter.items()])


    def flatten(self):
        """
        If the bag is a bag of collection then return the bag union of all
        its elements.

        :return: the sum of all elements .
        :rtype: int

        Examples:
            >>> Bag(Bag(2),Bag(3,3)).flatten() == Bag(2,3,3)
            True
            >>> Bag(Bag(),Bag(),Bag(3,2),Set(3)).flatten()  == Bag(3,2,3)
            True
        """
        counter = Counter()
        for (e,n) in self.theCounter.items():
            if isCollection(e):
                coll = e.flatten()
            else:
                coll = [e]
            for x in coll:
                counter[x] += n
        self.theCounter = counter
        return self

    def select(self,predicate):
        """
        Retain in the bag only the elements that satisfy the predicate.

        :param predicate: A predicate, that is a function returning a boolean.
        :return: The bag with only the selected elements.
        :rtype Bag:

        Examples:
            >>> Bag(2,3,2,3,-1,-2).select(lambda e:e>=0) == Bag(2,2,3,3)
            True
            >>> Bag().select(lambda e:True) == Bag()
            True
        """
        fresh = \
            Counter(dict([(e,n) for (e,n) in self.theCounter.items()
                          if evaluatePredicate(e,predicate)]))
        return Bag.new(fresh)

    def collectNested(self,expression):
        """
        Return a bag of values resulting from the evaluation of the given
        expression on all elements of the bag.

        It is assumed that the expression has no side effect; this
        expression is not called for each occurrence but only one for a
        given value. This is an optimisation for bags.

        :param expression: A function returning any kind of value.
        :type expression: X -> Y
        :return: The bag of values produced.
        :rtype Bag[Y]:

        Examples:
            >>> Bag(2,2,3,5,-5).collectNested(lambda e:e*e) == Bag(4,4,9,25,25)
            True
            >>> Bag(2,2).collectNested(lambda e:Bag(e,e)) \
                    == Bag(Bag(2,2),Bag(2,2))
            True
        """
        results = [(evaluate(e,expression),n)
                   for (e,n) in self.theCounter.items()]
        fresh = Counter()
        for (r,n) in results:
            fresh[r] += n
        return Bag.new(fresh)

    def hasDuplicates(self):
        """
        Return True if this bag has at least one element with more than one
        occurrence.

        This is not an OCL operation. It is provided here just for convenience.
        :return: True if there are some duplicates in the bag.
        :rtype: bool

        Examples:
            >>> Bag().hasDuplicates()
            False
            >>> Bag(2,3).hasDuplicates()
            False
            >>> Bag(2,2,1,3,3).hasDuplicates()
            True
        """
        for n in self.theCounter.values():
            if n > 1:
                return True
        return False

    def duplicates(self):
        """
            >>> Bag().duplicates() == Bag()
            True
            >>> Bag(2,3).duplicates() == Bag()
            True
            >>> Bag(2,2,1,3,3).duplicates()  == Bag(2,2,3,3)
            True
            """
        new_counter = \
            Counter(dict([(e,n) for (e,n) in self.theCounter.items() if n>=2]))
        return Bag.new(new_counter)


    def sortedBy(self,expression):
        r = []
        s = sorted(self.theCounter.keys(),key=lambda e:evaluate(e,expression))
        for key in s:
            r += [key] * self.theCounter[key]
        # FIXME: Should be an ordered set
        return r

    def asSet(self):
        return Set.new(self.theCounter.keys())

    def asBag(self):
        return self

    def asSeq(self):
        # A list with duplicates is wanted, so use elements().
        return Seq.new(list(self.theCounter.elements()))

    def __str__(self):
        return "Bag(%s)" % str(self.theCounter)

    def __repr__(self):
        return self.__str__()

    def __eq__(self,value):
        """
        Return True only if the value is a Bag with the same elements and
        number of occurrences.

        :param value: Any value.
        :type value: any
        :return: True if the value is equals to this bag.
        :rtype: bool

        Examples:
            >>> Bag(1,2,2) == Bag(2,2,1)
            True
            >>> Bag() == Bag()
            True
            >>> Bag(Bag(2,2)) == Bag(2,2)
            False
            >>> Bag(Set(2))==Bag(Set(2))
            True
        """
        if not isinstance(value,Bag):
            return False
        return self.theCounter == value.theCounter

    def __ne__(self,value):
        return not self.__eq__(value)

    def __hash__(self):
        return hash(tuple(self.theCounter.items()))

    def __iter__(self):
        """ Make Bags iterable for pythonic usage.
        :return: the iterator for this Bag
        :rtype: iterator

        Examples:
            >>> list(Bag())
            []
            >>> sorted(list(Bag(1,1,"a","b",1)))
            [1, 1, 1, 'a', 'b']
        """
        return self.theCounter.elements().__iter__()

    def __contains__(self,value):
        return self.theCounter[value] > 0




#------------------------------------------------------------------------------
#   OCL Sequences
#------------------------------------------------------------------------------

def asSeq(anyCollection):
    """
    Convert the given collection to a Seq
    :param anyCollection:
    :return:
    :rtype: Seq
    """

    try:
        return anyCollection.asSeq()
    except AttributeError:
        return Seq.new(anyCollection)


class Seq(Collection):
    def __init__(self,*args):
        """
        Create a Seq from some elements or from one collection.

        Examples:
           >>> Seq(10,"a",3,10,10) == Seq(10,10,"a",3,10)
           False
           >>> Seq(2) <> Seq(2,2,2)
           True
           >>> Seq(3,3,4) == Seq(3,4,3)
           False
           >>> Seq() == Seq()
           True
           >>> Seq() == Set()
           False
           >>> Seq(Seq(1,2)) == Seq(Seq(1),Seq(2))
           False
        """
        super(Seq,self).__init__()
        # no worry with args being a Counter
        self.theList = list(args)

    @classmethod
    def new(cls,anyCollection=()):
        newSeq = Seq()
        newSeq.theList = listAll(anyCollection)
        return newSeq

    def emptyCollection(self):
        return Seq.new()

    def size(self):
        return len(self.theList)

    def isEmpty(self):
        return True if self.theList else False

    def count(self,element):
        return self.theList.count(element)

    def includes(self,element):
        return element in self.theList

    def including(self,value):
        self.theList.append(value)
        return self

    def excluding(self,value):
        """
        Excludes all occurrence of the value from the sequence (if there).
        :param value: The element to add to the set.
        :type value: any
        :return: A set including this element.
        :rtype: Set
        Examples:
            >>> Seq(1,3,"a").excluding("3") == Seq(1,3,"a")
            True
            >>> Seq(1,3,3,2,3).excluding(3) == Seq(1,2)
            True
            >>> Seq().excluding(23) == Seq()
            True
        """
        return Seq.new([e for e in self.theList if e != value])

    def select(self,predicate):
        return Seq.new([e for e in self.theList
                        if evaluatePredicate(e,predicate)])

    def hasDuplicates(self):
        """
        Indicates if there duplicated elements in the sequence.

        This method is an extension to OCL. I
        :return: True
        :rtype: bool
        """
        return Bag.new(self).hasDuplicates()

    def duplicates(self):
        return Bag.new(self).duplicates()

    def flatten(self):
        r = []
        for e in self.theList:
            if isCollection(e):
                flat_list = listAll(flatten(e))
            else:
                flat_list = [e]
            r = r + flat_list
        self.theList = r
        return self


    def collectNested(self,expression):
        return Seq.new(map((lambda e:evaluate(e,expression)),self.theList))

    def sortedBy(self,expression):
        return \
            Seq.new(sorted(self.theList,key=(lambda e:evaluate(e,expression))))

    def union(self,anyCollection):
        assert isCollection(anyCollection), \
            'Any collection expected, but found %s' % anyCollection
        return Seq.new(self.theList + listAll(anyCollection))

    def __add__(self,anyCollection):
        return self.union(anyCollection)

    def append(self,value):
        fresh = list(self.theList)
        fresh.append(value)
        return Seq.new(fresh)

    def prepend(self,value):
        fresh = list(self.theList)
        fresh.insert(0,value)
        return Seq.new(fresh)

    def subSequence(self,lower,upper):
        try:
            return Seq.new(self.theList[lower - 1:upper])
        except:
            msg = ".subSequence(%s,%s) failed: No such element."
            raise Invalid(msg % (lower,upper))

    def at(self,index):
        """
        Return the nth element of the sequence starting from 1.

        Note: In OCL the 1st element is at the index 1 while in python this
        is at 0. Both the OCL 'at' and python [] operators can be used,
        but remember the different way to index elements.

        Examples:
            >>> Seq(1,2,3,4).at(1)
            1
            >>> Seq(1,2,3,4)[0]
            1

        :param index: The index of the element to return, starting at:

         * 1 for the OCL 'at' operator.
         * 0 for the [] python operator.

        :type: int
        :return: The element at that position.
        :rtype: any
        """
        try:
            return self.theList[index - 1]
        except:
            raise Invalid(".at(%s) failed: No such element." % index)


    def __getitem__(self,item):
        return self.theList[item]

    def asSet(self):
        return Set.new(self.theList)

    def asBag(self):
        return Bag.new(self.theList)

    def asSeq(self):
        return self

    def first(self):
        try:
            return self.theList[0]
        except:
            raise Invalid(".first() failed: No such element.")


    def last(self):
        try:
            return self.theList[-1]
        except:
            raise Invalid(".last() failed: No such element.")


    def __str__(self):
        return 'Seq(%s)' % self.theList

    def __repr__(self):
        return self.__str__()

    def __eq__(self,value):
        if not isinstance(value,Seq):
            return False
        return self.theList == value.theList

    def __hash__(self):
        return hash(tuple(self.theList))

    def __contains__(self,item):
        return item in self.theList

    def __iter__(self):
        return self.theList.__iter__()







#==============================================================================
#     Conversions
#==============================================================================




import collections


class ConversionRule(object):
    def __init__(self,language,sourceType,collectionType):
        self.language = language
        self.sourceType = sourceType
        self.collectionType = collectionType
    def accept(self,value):
        return isinstance(value,self.sourceType)
    def asCollection(self,value):
        return self.collectionType.new(value)
    def emptyCollection(self):
        return self.collectionType.new()

from collections import OrderedDict


class Converter(object):
    def __init__(self):
        self.rules = OrderedDict()
        self.language_collections = OrderedDict()
        self.all_collections = []

    def registerConversionRules(self,language,conversionList):
        for (source,target) in conversionList:
            rule = ConversionRule(language,source,target)
            self.rules[source] = rule
            if language not in self.language_collections:
                self.language_collections[language] = []
            self.language_collections[language].append(source)
            self.all_collections.append(source)

    def _registerActualTypeRule(self,source,rule):
        self.registerConversionRules(
            self,rule.language,[(source,rule.collectionType)])
        return self.rules[source]

    def isCollection(self,value,language=None):
        if isinstance(value,basestring):
            return False
        if language == None:
            collections = self.all_collections
        else:
            collections = self.language_collections[language]
        return isinstance(value,tuple(collections))

    def findRule(self,value):
        """
        Return the type of the OCL collection corresponding to the given type.

        Raise an exception if no conversion is possible for the given type
        :param aType: The type to be converted.
        :type aType: type
        :return: A collection type.
        :rtype: type < Collection
        :raise: ValueError if there is no correspondance possible.
        """
        valueType = type(value)
        # check if we have some chance and the type is already registered
        if valueType in self.rules:
            return self.rules[valueType]
        else:
            # no chance. We have to check if this is a subtype.
            for rule in self.rules.values():
                if rule.accept(value):
                    return self._registerActualTypeRule(self,valueType,rule)
            msg = "getConversionRule(): Can't convert a value of type %s"
            raise ValueError(msg % valueType)

    def asCollection(self,value):
        try:
            return value.asCollection()
        except AttributeError:
            return self.findRule(value).asCollection(value)

    def emptyCollection(self,value):
        try:
            return value.emptyCollection()
        except NameError:
            return self.findRule(value).emptyCollection(value)

    def listAll(self,value):
        """
        Return all the elements of the collection as a list.

        This takes into account the Counter specificity: instead of using
        list and the standard enumeration on this collection this function
        use the "elements()" method. Otherwise occurrences are eliminated.
        """
        if isinstance(value,collections.Counter):
            return list(value.elements())
        else:
            return list(value)

CONVERTER = Converter()

pythonConversionRules = [   # Order is very important
    (set,Set),
    (frozenset,Set),
    (collections.Counter,Bag),
    (list,Seq),
    (tuple,Seq),
    (collections.deque,Seq),
    (collections.Iterable,Seq),
    (collections.Iterable,Seq),
]
CONVERTER.registerConversionRules('python',pythonConversionRules)

oclConversionRules = [
    (Set,Set),
    (Bag,Bag),
    (Seq,Seq),
]
CONVERTER.registerConversionRules('ocl',oclConversionRules)



def asCollection(anyCollection):
    """
    Convert any collection into the proper (OCL) collection.

    :param anyCollection: A python, java or ocl collection.
    :return: The OCL collection
    :rtype: Collection

    Examples:
        >>> asCollection({2,3}) == Set(3,2)
        True
        >>> asCollection(frozenset({1,5,1})) == Set(1,5)
        True
        >>> asCollection(Counter([1,1,3,1])) == Bag(1,1,1,3)
        True
        >>> asCollection(Counter({'hello':2,-1:0})) == Bag('hello','hello')
        True
        >>> asCollection([1,2,3,4]) == Seq(1,2,3,4)
        True
        >>> asCollection((1,2,3,4)) == Seq(1,2,3,4)
        True
        >>> asCollection(deque([1,2,3,4])) == Seq(1,2,3,4)
        True
    """
    return CONVERTER.asCollection(anyCollection)

def emptyCollection(anyCollection):
    return CONVERTER.emptyCollection(anyCollection)

def listAll(collection):
    return CONVERTER.listAll(collection)

def isCollection(value,language=None):
    """

    :param value:
    :param language:
    :return:
        >>> isCollection((2,3))
        True
        >>> isCollection([])
        True
        >>> isCollection(12)
        False
        >>> isCollection(Counter())
        True
        >>> isCollection("text")
        False
    """
    return CONVERTER.isCollection(value,language=language)


# def asCollection(anyCollection):
#     if isCollection(anyCollection):
#         return anyCollection
#     elif isJavaCollection(anyCollection):
#         pass




# execute tests if launched from command line
if __name__ == "__main__":
    import doctest
    doctest.testmod()

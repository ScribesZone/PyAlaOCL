# coding=utf-8


class Fragment(object):
    """
    A fragment is a decorated
    """
    def __init__(self, start, end=None, value=None,
                 parent=None, children=None):
        self.start = start
        """ The index of the beginning of the fragment """

        self.end = end  # could be None during fragmentation time, not after
        """ The index of the end of the fragment """

        self.value = value
        """ The value associated with the fragment """

        self.parent = parent
        """ The parent of this fragment or None if this is the root """
        if parent is not None and self not in parent.children:
            parent.children.append(self)

        self.children = [] if children is None else children
        """ The children of this fragment """


    def addChild(self, fragment):
        self.children.append(fragment)
        fragment.parent = self

    def range(self):
        return (self.start, self.end)

    def rangeAndValue(self):
        return ((self.start, self.end), self.value)

    def ancestors(self, includingSelf=False):
        if self.parent is None:
            return [] if not includingSelf else [self]
        else:
            return self.parent.parents() + [self.parent]

    def descendants(self, includingSelf=False):
        _ = [] if not includingSelf else [self]
        for child in self.children:
            _ += [child] + child.descendants()
        return _

    def depth(self, includingSelf=False):
        _ = 0 if not includingSelf else 1
        for child in self.children:
            _ = max(_, child.depth() + 1)
        return _

    def fragmentsOfValue(self, value):
        if self.value == value:
            return [self]
        _ = []
        for child in self.children:
            _ += child.fragmentsOfValue(value)
        return _

    def fragmentAtPosition(self, position):
        if position < self.start or self.end < position:
            return None
        for child in self.children:
            f = child.fragmentAtPosition(position)
            if f is not None:
                return f
        return self

    def fragmentsAtPosition(self, position):
        if position < self.start or self.end < position:
            return []
        for child in self.children:
            fs = child.fragmentsAtPosition(position)
            if fs != []:
                return fs + [self]
        return [self]

    def __repr__(self):
        return 'Fragment({start}-{end}:{value},{children})'.format(
            start=self.start,
            end=self.end,
            value=self.value,
            children=self.children
        )






#------------------------------------------------------------------------------
#      Fragmentation
#------------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod


class Fragmenter(object):
    """
    Abstract base class for fragmenters.
    """
    __metaclass__ = ABCMeta

    def __init__(self, sequence, mainValue=None, firstPosition=1 ):
        """

        :param sequence: A sequence of arbitrary elements.
        :type sequence: [X]
        :param mainValue: Any value attached to the main fragment
        :type mainValue: Y
        :param firstPosition: The position of the first element (e.g. 0 or 1)
        :type firstPosition: int
        :return: aa fragmenter object. Use  f = Fragmenter(...).fragment
        :rtype: Fragmenter

        """
        self.sequence = sequence
        self.first_position = firstPosition
        self.last_position = len(sequence) - 1 + firstPosition
        self.fragment = Fragment(firstPosition, self.last_position, mainValue)
        self.__doFragment()


    def __doFragment(self):
        position = self.first_position
        enclosing_fragments = [self.fragment]
        for element in self.sequence:

            value = self.opening(element, enclosing_fragments)
            if value is not None:
                f = Fragment(start=position, end=None, value=value,
                             parent=enclosing_fragments[-1],
                             children=[])
                enclosing_fragments.append(f)

            value = self.closing(element, enclosing_fragments, value)
            if value is not None:
                f = enclosing_fragments[-1]
                f.end = position
                del enclosing_fragments[-1]

            value = self.here(element, enclosing_fragments)
            if value is not None:
                f = Fragment(start=position, end=position, value=value,
                             parent=enclosing_fragments[-1],
                             children=[])

            position += 1


    @abstractmethod
    def opening(self, element, enclosingFragments):
        pass


    @abstractmethod
    def closing(self, element, enclosingFragments, value=None):
        pass


    @abstractmethod
    def here(self, element, enclosingFragments):
        pass



import re

class RegexpFragmenter(Fragmenter):
    def __init__(self, sequence,
                 openingRegexp=r'--oo<< *(?P<value>[^ \n]+) *$',
                 closingRegexp=r'--oo>> *$',
                 hereRegexp=r'--oo== *(?P<value>[^ \n]+) *$',
                 mainValue=None, firstPosition=1):
        """
            >>> text = [
            ... 'First line',
            ... 'This is a text --oo<<first_sentence',
            ... 'with some',
            ... 'markers. --oo>>',
            ... 'We start --oo<< block',
            ... 'something with',
            ... 'more text',
            ... 'and a figure. --oo== figure1',
            ... 'With a nested --oo<< nested',
            ... 'block. --oo>>',
            ... 'Closing block. --oo>>',
            ... 'This is the end --oo== end',
            ... ]
            >>> print len(text)
            12
            >>> fragment = RegexpFragmenter(text,mainValue='main').fragment
            >>> print len(fragment.descendants(True))
            6
            >>> print fragment.depth()
            2
            >>> print fragment.fragmentsOfValue('not there')
            []
            >>> print fragment.fragmentsOfValue('nested')
            [Fragment(9-10:nested,[])]
            >>> print fragment.fragmentAtPosition(2).value
            first_sentence
            >>> print fragment.fragmentAtPosition(10).value
            nested
            >>> print fragment.fragmentAtPosition(1).value
            main
            >>> print fragment.fragmentAtPosition(1000)
            None
            >>> def values(sequence) : return map(lambda f:f.value, sequence)
            >>> print values(fragment.fragmentsAtPosition(1))
            ['main']
            >>> print values(fragment.fragmentsAtPosition(10))
            ['nested', 'block', 'main']
            >>> print values(fragment.fragmentsAtPosition(1000))
            []



        """
        self.openingRegexp = openingRegexp
        self.closingRegexp = closingRegexp
        self.hereRegexp = hereRegexp
        # must be after the assignments above since this trigger analysis
        super(RegexpFragmenter, self).__init__(
            sequence, mainValue=mainValue, firstPosition=firstPosition)


    def opening(self, element, enclosingFragments):
            m = re.search(self.openingRegexp, element)
            if m:
                return m.group('value')
            else:
                return None

    def closing(self, element, enclosingFragments, value=None):
        m = re.search(self.closingRegexp, element)
        m = re.search(self.closingRegexp, element)
        if m:
            # here we could change the semantics and check for value equality
            return True
        else:
            return None

    def here(self, element, enclosingFragments):
        m = re.search(self.hereRegexp, element)
        if m:
            return m.group('value')
        else:
            return None



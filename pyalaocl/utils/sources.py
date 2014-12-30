# coding=utf-8

import os

import pyalaocl.utils.fragments

class SourceFile(object):
    """
    A source file seen as as sequence of lines. The source file may contains
    some list of errors.
    """
    def __init__(self, fileName):
        if not os.path.isfile(fileName):
            raise Exception('File "%s" not found' \
                            % fileName)

        self.fileName = fileName
        """ The filename as given when creating the source file"""

        self.name = \
            os.path.splitext(os.path.basename(self.fileName))[0]
        """ The short file name with extension included """

        f = open(fileName, 'r')
        self.sourceLines = tuple(f.read().splitlines())
        """ The list of lines of the source file"""
        f.close()

        self.errors = []
        """ The list of errors """

    def addError(self, sourceError):
        self.errors.append(sourceError)

    def clearErrors(self):
        self.errors = []

    def __repr__(self):
        return ('SourceFile(%s)'%self.fileName)



class AnnotatedSourceFile(SourceFile):
    """
    A source file with annotated fragments. The source can be viewed
    both as a flat sequence of line or as a fragment trees.
    The annotation markers can be defined when building the source file.
    """
    def __init__(self, fileName,
                 openingMark = r'--oo<< *(?P<value>[^ \n]+) *$',
                 closingMark = r'--oo>> *$',
                 hereMark = r'--oo== *(?P<value>[^ \n]+) *$'):
        """
        Create a annotated source file. The mark have to be provided
        in the form of regular expression with sometimes an optional
        named group with the named value. That is a regexp group like
        (?P<value> ... ). This part will be extracted and will
        constitute the name of the mark.
        :param fileName: the file name
        :type fileName: str
        :param openingMark: The opening mark with ?P<value> group
        :type openingMark: str
        :param closingMark: The closing mark
        :type closingMark: str
        :param hereMark: The here mark with ?P<value> group
        :type hereMark: str
        :return: AnnotatedSourceFile
        :rtype: AnnotatedSourceFile
        """

        super(AnnotatedSourceFile,self).__init__(fileName)
        self.openingMark = openingMark
        self.closingMark = closingMark
        self.hereMark = hereMark

        fragmenter = pyalaocl.utils.symbols.RegexpFragmenter(
            self.sourceLines,
            openingMark, closingMark, hereMark,
            mainValue = self, firstPosition = 1)

        self.fragment = fragmenter.fragment
        """ The root fragment according to the given mark """

    def __repr__(self):
        return ('AnnotatedSourceFile(%s)'%self.fileName)





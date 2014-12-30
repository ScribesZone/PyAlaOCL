# coding=utf-8

import sources

class SourceError(object):
    """
    An error in a given source file. Direct instances of SourceError
    are not localized within the source. Use Localized Error instead
    if the error line is known.
    """
    def __init__(self, sourceFile, message):
        """
        Create a source error and add it to the given source file.
        :param sourceFile: The source file
        :type sourceFile: SourceFile
        :param message: The error message
        :type message: str
        :return: SourceError
        :rtype: SourceError
        """
        self.sourceFile = sourceFile
        """ The source file. An instance of SourceFile. """

        self.message = message
        """ The error message. """

        self.sourceFile.addError(self)


    def description(self, pattern='ERROR:{message}'):
        """
        Display the error. Since the error is not localized
        direct instances of this class just display the error message.
        Subclasses provide more useful information
        """
        return pattern.format(message=self.message)


    def __str__(self):
        return self.description()


    def __repr__(self):
        return self.__str__()



class LocalizedError(SourceError):

    #FIXME: sourceFile is given, and fileName as well?
    def __init__(self, sourceFile, message, line, column, fileName=None):
        """
        Create a localized source file and add it to the given source file.
        :param sourceFile: The Source File
        :type sourceFile: SourceFile
        :param message: The error message.
        :type message: str
        :param line: The line number of the error starting at 1. If the
        error is before the first line, 0 is an accepted value though.
        :type line: int
        :param column: The column number of the error or None. If the error
        is between the previous line and before the first column 0 is an
        acceptable value.
        :type column: int|NoneType
        :param fileName: An optional string representing the filename as
        to be output with the error message. If None is given, then this
        value will be taken from the source file.
        :type fileName: str|NoneType
        :return: LocalizedError
        :rtype: LocalizedError
        """
        super(LocalizedError, self).__init__(sourceFile, message)

        self.sourceFile = sourceFile
        """ The source file. An instance of SourceFile. """

        self.fileName = fileName
        self.line = line
        self.column = column


    def description(self, pattern='{file}:{line}:{column}: {message}',
                    showSource=True, linesBefore=1, linesAfter=0 ):
        _ = []
        if showSource:
            if linesBefore >=1:
                begin = max(0, self.line - linesBefore)
                end = self.line
                _ += self.sourceFile.sourceLines[begin:end]

            cursor_line = \
                '_'*(self.column - 1) \
                + '|' \
                + '_'*(len(self.sourceFile.sourceLines[
                                max(0,self.line-1)])-self.column)
            _ += cursor_line

            if linesAfter:
                begin = self.line - 1
                end = max(len(self.sourceFile.sourceLines)-1,self.line+linesAfter-1)
                _ += self.sourceFile.sourceLines[begin:end]

        error = pattern.format(file=self.fileName, line=self.line,
                               column=self.column, message=self.message )
        _ += error

        return '\n'.join(_)


    def __str__(self):
        return '%s:%s:%s: %s' \
               % (self.fileName, self.line, self.column, self.message)


    def __repr__(self):
        return self.__str__()


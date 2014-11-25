# coding=utf-8

class UseOclError(object):
    def __init__(self, specification, message):
        self.specification = specification
        self.message = message

    def __str__(self):
        return 'ERROR:%s' % self.message

    def __repr__(self):
        return self.__str__()


class LocalizedError(UseOclError):
    def __init__(self, specification, message, filename, line, column):
        super(LocalizedError, self).__init__(specification, message)
        self.line = line
        self.column = column
        self.filename = filename
        if self.line > len(self.specification.source_lines):
            self.source_line = ''
        else:
            self.source_line = self.specification.source_lines[self.line - 1]

    def __str__(self):
        return '%s\n%s\n%s:%s:%s: %s' \
               % (self.source_line,
                  ' ' * (self.column - 1) + '^',
                  self.filename, self.line, self.column, self.message)

    def __repr__(self):
        return self.__str__()

print'pyalaocl.useocl.errors reloaded'

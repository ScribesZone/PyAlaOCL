# coding=utf-8

import os
import re

import pyalaocl.utils.errors
import pyalaocl.utils.sources
import pyalaocl.useocl.useengine
import pyalaocl.useocl.model
#from pyalaocl.useocl.model import Model, Enumeration, Class, Attribute, \
#    Operation, Invariant, Association, Role, AssociationClass, \
#    PreCondition, PostCondition, BasicType

class UseOCLModel(pyalaocl.utils.sources.SourceFile):
    def __init__(self, useModelSourceFile):
        super(UseOCLModel, self).__init__(useModelSourceFile)
        self.isValid = None  # Don't know yet
        self.canonicalLines = None  # Nothing yet
        self.canonicalLength = 0  # Nothing yet
        self.errors = []  # No errors yet
        self.commandExitCode = None  # Nothing yet
        self.model = None  # Nothing yet, created by parse/resolve
        # Try to validate the model and fill
        #       self.isValid
        #       self.errors,
        #       self.commandExitCode,
        #       self.canonicalLines,
        #       self.canonicalLength
        self.__createCanonicalForm()
        if self.isValid:
            # Create the model by parsing the canonical form
            # fill  self.model,
            self.__parseCanonicalLinesAndCreateModel()
            self.__resolveModel()

    def saveCanonicalModelFile(self, fileName=None):
        if fileName is None:
            fileName = os.path.splitext(self.fileName)[0] + '.can.use'
        f = open(fileName, 'w')
        f.write('\n'.join(self.canonicalLines))
        f.close()
        return fileName


    #--------------------------------------------------------------------------
    #    Class implementation
    #--------------------------------------------------------------------------

    def __createCanonicalForm(self):
        engine = pyalaocl.useocl.useengine.USEEngine
        self.commandExitCode = engine.analyzeUSEModel(self.fileName)
        if self.commandExitCode != 0:
            self.isValid = False
            self.errors = []
            for line in engine.err.splitlines():
                self.errors.append(self.__parseErrorLine(line))
        else:
            self.isValid = True
            self.errors = []
            # Remove 2 lines at the beginning (use intro + command)
            # and two lines at the end (information + quit command)
            self.canonicalLines = engine.out.splitlines()[2:-2]
            self.canonicalLength = len(self.canonicalLines)
        return self.isValid

    def __parseErrorLine(self, line):
        p = r'^(?P<filename>.*)' \
            r'(:|:line | line )(?P<line>\d+):(?P<column>\d+)(:)?' \
            r'(?P<message>.+)$'
        m = re.match(p, line)
        if m:
            # print 'ERROR', line
            return pyalaocl.utils.errors.LocalizedError(
                self,
                m.group('message'),
                int(m.group('line')),
                int(m.group('column'),
                m.group('filename')),
            )
        else:
            return pyalaocl.utils.errors.SourceError(self, line)


    def __parseCanonicalLinesAndCreateModel(self):
        # self.__matches = None
        # self.__i = 0
        #
        # def until(regexp, force=True):
        #     self.__matches = None
        #     while self.__i < self.canonicalLength:
        #         print self.__i, ':', self.canonicalLines[self.__i]
        #         self.__matches = re.match(regexp,
        #                                   self.canonicalLines[self.__i])
        #         if self.__matches is not None:
        #             break
        #         else:
        #             self.__i += 1
        #     if self.__matches is None and force:
        #         raise Exception(
        #             'Error in parsing. Waiting for a line matching %s'
        #             % regexp)

        current_class = None
        current_association = None
        current_invariant = None
        current_operation = None
        current_operation_condition = None

        for line in self.canonicalLines:
            # print '==',line
            r = r'^(constraints' \
                r'|attributes' \
                r'|operations' \
                r'|    begin' \
                r'|    end' \
                r'|' \
                r'|( *@(Test|Monitor)\(.*\)))$'
            m = re.match(r, line)
            if m:
                # these lines can be ignored
                continue

            #---- model --------------------------------------------------
            r = r'^model (?P<name>\w+)$'
            m = re.match(r, line)
            if m:
                self.model = pyalaocl.useocl.model.Model(
                    name=m.group('name'),
                    code=self.sourceLines)
                continue

            #---- enumeration --------------------------------------------
            r = r'^enum (?P<name>\w+) { (?P<literals>.*) };?$'
            m = re.match(r, line)
            if m:
                pyalaocl.useocl.model.Enumeration(
                    name=m.group('name'),
                    model=self.model,
                    code=line,
                    literals=m.group('literals').split(', '))
                continue

            #---- class --------------------------------------------------
            r = r'^((?P<abstract>abstract) )?class (?P<name>\w+)' \
                r'( < (?P<superclasses>(\w+|,)+))?$'
            m = re.match(r, line)
            if m:
                # parse superclasses series
                if m.group('superclasses') is None:
                    superclasses = ()
                else:
                    superclasses = m.group('superclasses').split(',')
                current_class = \
                    pyalaocl.useocl.model.Class(
                        name=m.group('name'),
                        model=self.model,
                        isAbstract=m.group('abstract') == 'abstract',
                        superclasses=superclasses
                    )
                continue

            #---- associationclass ---------------------------------------
            r = r'^((?P<abstract>abstract) )?associationclass (?P<name>\w+)' \
                r'( < (?P<superclasses>(\w+|,)+))?' \
                r' between$'
            m = re.match(r, line)
            if m:
                # parse superclasses series
                if m.group('superclasses') is None:
                    superclasses = ()
                else:
                    superclasses = m.group('superclasses').split(',')
                ac = \
                    pyalaocl.useocl.model.AssociationClass(
                        name=m.group('name'),
                        model=self.model,
                        isAbstract=m.group('abstract') == 'abstract',
                        superclasses=superclasses
                    )
                current_class = ac
                current_association = ac
                continue

            #---- attribute ----------------------------------------------
            r = r'^  (?P<name>\w+) : (?P<type>\w+)$'
            m = re.match(r, line)
            if m:
                if current_class is not None:
                    # This could be an association class
                    pyalaocl.useocl.model.Attribute(
                        name=m.group('name'),
                        class_=current_class,
                        code=line,
                        type=m.group('type'))
                    continue

            #---- operation ----------------------------------------------
            r = r'^  (?P<name>\w+)' \
                r'(?P<params_and_result>[^=]*)' \
                r'( = )?$'
            # r = r'^  (?P<name>\w+)' \
            #    r'\((?P<parameters>.*)\)' \
            #    r'( : (?P<type>(\w|,|\))+))?' \
            #    r'( =)?'
            m = re.match(r, line)
            if m:
                if current_class is not None:
                    # This could be an association class
                    operation = \
                        pyalaocl.useocl.model.Operation(
                            name=m.group('name'),
                            model=self.model,
                            class_=current_class,
                            code=line,
                            signature=m.group('name')
                                      + m.group('params_and_result'))
                    if line.endswith(' = '):
                        current_operation = operation
                    else:
                        current_operation = None
                    #print '==',line
                    #print '   ', operation.signature
                    #print '   "%s"' % operation.full_signature
                    #print

                    continue

            #---- operation expression -----------------------------------
            r = r'^    (?P<expression>[^ ].*)$'
            m = re.match(r, line)
            if m:
                if current_operation is not None:
                    # This could be an association class
                    current_operation.expression = m.group('expression')
                    continue

            #---- association --------------------------------------------
            r = r'^(?P<kind>association|composition|aggregation) ' \
                r'(?P<name>\w+) between$'
            m = re.match(r, line)
            if m:
                current_association = \
                    pyalaocl.useocl.model.Association(
                        name=m.group('name'),
                        model=self.model,
                        kind=m.group('kind'))
                continue

            #---- role ---------------------------------------------------
            r = r'^  (?P<type>\w+)\[(?P<cardinality>[^\]]+)\] ' \
                r'role (?P<name>\w+)' \
                r'( qualifier \((?P<qualifiers>(\w| |:|,)*)\))?' \
                r'(?P<subsets>( subsets \w+)*)' \
                r'( (?P<union>union))?' \
                r'( (?P<ordered>ordered))?' \
                r'( (derived = (?P<expression>.*)))?$'
            m = re.match(r, line)
            if m:
                if current_association is not None:
                    # This could be an association class
                    # Parse the cardinality string
                    c = m.group('cardinality').split('..')
                    if c[0] == '*':
                        min = 0
                        max = None
                    elif len(c) == 1:
                        min = int(c[0])
                        max = min
                    else:
                        min = int(c[0])
                        max = None if c[1] == '*' else int(c[1])
                    # Parse the 'subsets' series
                    if m.group('subsets') == '':
                        subsets = None
                    else:
                        #print '***************', line
                        #print '**  ',m.group('subsets')
                        subsets = m.group('subsets').split('subsets ')[1:]
                        #print s
                    # Parse the 'qualifiers' series
                    if m.group('qualifiers') is None:
                        qualifiers = None
                    else:
                        qualifiers = \
                            [tuple(q.split(' : '))
                             for q in m.group('qualifiers').split(', ')]
                    pyalaocl.useocl.model.Role(
                        name=m.group('name'),
                        association=current_association,
                        type=m.group('type'),
                        cardMin=min,
                        cardMax=max,
                        isOrdered=m.group('ordered') == 'ordered',
                        qualifiers=qualifiers,
                        subsets=subsets,
                        isUnion=m.group('union') == 'union',
                        expression=m.group('expression')
                    )
                    continue

            #---- invariant ----------------------------------------------
            r = r'^context (?P<vars>(\w| |,)+) : (?P<class>\w+)' \
                r'( (?P<existential>existential))? inv (?P<name>\w+):$'
            m = re.match(r, line)
            if m:
                variables = m.group('vars').split(', ')
                current_invariant = \
                    pyalaocl.useocl.model.Invariant(
                        name=m.group('name'),
                        model=self.model,
                        class_=m.group('class'),
                        variable=variables[0],
                        additionalVariables=variables[1:],
                        isExistential=
                        m.group('existential') == 'existential',
                    )
                continue

            #---- invariant expression -----------------------------------
            r = r'^  (?P<expression>[^ ].*)$'
            m = re.match(r, line)
            if m:
                if current_invariant is not None:
                    current_invariant.expression = m.group('expression')
                    current_invariant = None
                    continue

            #---- pre or post condition ----------------------------------
            r = r'^context (?P<class>\w+)::' \
                r'(?P<signature>\w+.*)$'
            m = re.match(r, line)
            if m:
                full_signature = \
                    '%s::%s' % (m.group('class'), m.group('signature'))
                operation = self.model.operations[full_signature]
                current_operation_condition = {
                    'class': m.group('class'),
                    'full_signature': full_signature,
                    'operation': operation
                }
                continue

            #---- body of pre or post condition --------------------------
            r = r'^  (?P<kind>(pre|post)) (?P<name>\w+): ' \
                r'(?P<expression>.*)$'
            m = re.match(r, line)
            if m:
                if current_operation_condition is not None:
                    operation = current_operation_condition['operation']
                    v = m.groupdict()
                    if v['kind'] == 'pre':
                        pyalaocl.useocl.model.PreCondition(
                            v['name'], self.model, operation, v['expression'])
                    else:
                        pyalaocl.useocl.model.PostCondition(
                            v['name'], self.model, operation, v['expression'])

                    current_operation_condition = None
                    continue

            #---- end of association, class, invariant or operation ------
            r = r'^(end)$'  # match empty line as well
            m = re.match(r, line)
            if m:
                current_class = None
                current_association = None
                continue

            #---- a line has not been processed.
            self.isValid = False
            self.errors.append('Parser: cannot process line "%s"' % line)


    def __resolveModel(self):

        def __resolveSimpleType(name):
            """ Search the name in enumeration of basic type or register it.
            """
            if name in self.model.enumerations:
                return self.model.enumerations[name]
            elif name in self.model.basicTypes:
                return self.model.basicTypes[name]
            else:
                self.model.basicTypes[name] = \
                    pyalaocl.useocl.model.BasicType(name)
                return self.model.basicTypes[name]

        def __resolveClassType(name):
            """ Search in class names or association class names.
            """
            if name in self.model.classes:
                return self.model.classes[name]
            else:
                return self.model.associationClasses[name]

        def __resolveAttribute(attribute):
            # Resolve the attribute type
            attribute.type = __resolveSimpleType(attribute.type)

        def __resolveOperation(operation):
            # TODO: implement parsing of parameters and result type
            raise NotImplementedError('operation resolution not implemented')

        def __resolveClass(class_):
            # resolve superclasses
            class_.superclasses = \
                [__resolveClassType(name) for name in class_.superclasses]
            # resolve class attributes
            for a in class_.attributes.values():
                __resolveAttribute(a)
            # resolve class operations
            for op in class_.operations:
                pass  # TODO

        def __resolveSubsets(role):
            # TODO: implement subsets role search
            raise NotImplementedError('subset resolution not implemented')

        def __resolveRole(role):
            # resolve role type
            role.type = __resolveClassType(role.type)
            # resolve qualifier types
            if role.qualifiers is not None:
                qs = role.qualifiers
                role.qualifiers = []
                for (n, t) in qs:
                    role.qualifiers.append((n, __resolveSimpleType(t)))
            if role.subsets is not None:
                for s in role.subsets:
                    pass  # TODO _resolveSubset(role)
            if role.association.isBinary:
                rs = role.association.roles.values()
                role.opposite = rs[1] if role is rs[0] else rs[0]

        def __resolveAssociation(association):
            association.arity = len(association.roles)
            association.isBinary = (association.arity == 2)
            for role in association.roles.values():
                __resolveRole(role)

        def __resolveInvariant(invariant):
            c = __resolveClassType(invariant.class_)
            invariant.class_ = c
            c.invariants[invariant.name] = invariant

        # resolve class (and class part of class associations)
        cs = self.model.classes.values() \
             + self.model.associationClasses.values()
        for c in cs:
            __resolveClass(c)

        # resolve association (and association part of class association)
        as_ = self.model.associations.values() \
              + self.model.associationClasses.values()
        for a in as_:
            __resolveAssociation(a)

        # resolve invariant
        for i in self.model.invariants:
            __resolveInvariant(i)


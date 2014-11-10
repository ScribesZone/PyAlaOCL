# coding=utf-8

import os
import sys
import re
import tempfile
from alaocl.useocl.errors import Error, LocalizedError
from alaocl.useocl.model import Model, Enumeration, Class, Attribute,\
    Operation, Invariant, Association, Role, AssociationClass, \
    PreCondition, PostCondition, BasicType

USE_COMMAND = 'use'

class UseOCLSourceSpecification(object):
    def __init__(self, useSpecificationSourceFile):
        if not os.path.isfile(useSpecificationSourceFile):
            raise Exception('File "%s" not found' \
                            % useSpecificationSourceFile)
        self.source_file_name = useSpecificationSourceFile
        self.source_lines     = tuple(
            open(useSpecificationSourceFile, 'r').read().splitlines())



class UseOCLSpecification(UseOCLSourceSpecification):
    def __init__(self, useSpecificationSourceFile):
        super(UseOCLSpecification,self).__init__(useSpecificationSourceFile)
        self.isValid          = None  # Don't know yet
        self.canonical_lines  = None  # Nothing yet
        self.canonical_length = 0     # Nothing yet
        self.errors           = []    # No errors yet
        self.commandExitCode  = None  # Nothing yet
        self.model            = None  # Nothing yet
        self._createCanonicalForm()
        if self.isValid:
            self._parseCanonicalLines()
            self._resolveModel()

    def _createCanonicalForm(self):
        soil_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', '..', 'res', 'infoModelAndQuit.soil')
        (f, output_filename) = tempfile.mkstemp(suffix='.use', text=True)
        os.close(f)
        (f, errors_filename) = tempfile.mkstemp(suffix='.err', text=True)
        os.close(f)
        cmd = '%s -nogui %s %s >%s 2>%s' \
              % (USE_COMMAND, self.source_file_name, soil_file,
                 output_filename, errors_filename)
        # This should be safe, as we already tested that the user input
        # is a really a filename and do not contains dangerous characters.
        self.commandExitCode = os.system(cmd)
        if self.commandExitCode != 0:
            self.isValid = False
            self.errors = []
            for line in open(errors_filename, 'r').read().splitlines():
                self.errors.append(self._parseErrorLine(line))
        else:
            self.isValid = True
            self.errors = []
            output = open(output_filename, 'r').read()
            # Remove 2 lines at the beginning (use intro + command)
            # and two lines at the end (information + quit command)
            self.canonical_lines = output.splitlines()[2:-2]
            self.canonical_length = len(self.canonical_lines)
        os.remove(output_filename)
        os.remove(errors_filename)
        return self.isValid

    def _parseErrorLine(self, line):
        p = r'^(?P<filename>.*)' \
            r'(:|:line | line )(?P<line>\d+):(?P<column>\d+)(:)?' \
            r'(?P<message>.+)$'
        m = re.match(p, line)
        if m:
            return LocalizedError(
                self,
                m.group('message'),
                m.group('filename'),
                int(m.group('line')),
                int(m.group('column')),
            )
        else:
            return Error(self, line)

    def _parseCanonicalLines(self):
        # self.__matches = None
        # self.__i = 0
        #
        # def until(regexp, force=True):
        #     self.__matches = None
        #     while self.__i < self.canonical_length:
        #         print self.__i, ':', self.canonical_lines[self.__i]
        #         self.__matches = re.match(regexp,
        #                                   self.canonical_lines[self.__i])
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

        for line in self.canonical_lines:
            # print '==',line
            r = r'^(constraints' \
                r'|attributes'   \
                r'|operations'   \
                r'|    begin'    \
                r'|    end'      \
                r'|'             \
                r'|( *@(Test|Monitor)\(.*\)))$'
            m = re.match(r, line)
            if m:
                # these lines can be ignored
                continue

            #---- model --------------------------------------------------
            r = r'^model (?P<name>\w+)$'
            m = re.match(r, line)
            if m:
                self.model = Model(
                    name = m.group('name'),
                    code = self.source_lines)
                continue

            #---- enumeration --------------------------------------------
            r = r'^enum (?P<name>\w+) { (?P<literals>.*) };?$'
            m = re.match(r, line)
            if m:
                Enumeration(
                    name = m.group('name'),
                    model = self.model,
                    code = line,
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
                    Class(
                        name = m.group('name'),
                        model = self.model,
                        isAbstract = m.group('abstract') == 'abstract',
                        superclasses =superclasses
                    )
                continue

            #---- associationclass ---------------------------------------
            r = r'^((?P<abstract>abstract) )?associationclass (?P<name>\w+)'\
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
                    AssociationClass(
                        name=m.group('name'),
                        model=self.model,
                        isAbstract = m.group('abstract')=='abstract',
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
                    Attribute(
                        name   = m.group('name'),
                        class_ = current_class,
                        code   = line,
                        type   = m.group('type'))
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
                    operation =\
                        Operation(
                            name = m.group('name'),
                            model = self.model,
                            class_ = current_class,
                            code = line,
                            signature =   m.group('name')
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
                    Association(
                        name  = m.group('name'),
                        model = self.model,
                        kind  = m.group('kind'))
                continue

            #---- role ---------------------------------------------------
            r = r'^  (?P<type>\w+)\[(?P<cardinality>[^\]]+)\] ' \
                r'role (?P<name>\w+)' \
                r'( qualifier \((?P<qualifiers>(\w| |:|,)*)\))?' \
                r'(?P<subsets>( subsets \w+)*)' \
                r'( (?P<union>union))?' \
                r'( (?P<ordered>ordered))?'\
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
                        max = None if c[1]=='*' else int(c[1])
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
                                for q in  m.group('qualifiers').split(', ')]
                    Role(
                        name        = m.group('name'),
                        association = current_association,
                        type        = m.group('type'),
                        cardMin     = min,
                        cardMax     = max,
                        isOrdered   = m.group('ordered') == 'ordered',
                        qualifiers  = qualifiers,
                        subsets     = subsets,
                        isUnion     = m.group('union') == 'union',
                        expression  = m.group('expression')
                    )
                    continue

            #---- invariant ----------------------------------------------
            r = r'^context (?P<vars>(\w| |,)+) : (?P<class>\w+)' \
                r'( (?P<existential>existential))? inv (?P<name>\w+):$'
            m = re.match(r, line)
            if m:
                variables=m.group('vars').split(', ')
                current_invariant = \
                    Invariant(
                        name   = m.group('name'),
                        model  = self.model,
                        class_ = m.group('class'),
                        variable = variables[0],
                        additionalVariables=variables[1:],
                        isExistential =
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
                    'class' : m.group('class'),
                    'full_signature' : full_signature,
                    'operation' : operation
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
                        PreCondition(
                            v['name'], self.model, operation, v['expression'])
                    else:
                        PostCondition(
                            v['name'], self.model, operation, v['expression'])

                    current_operation_condition = None
                    continue

            #---- end of association, class, invariant or operation ------
            r = r'^(end)$'   # match empty line as well
            m = re.match(r, line)
            if m:
                current_class = None
                current_association = None
                continue

            #---- a line has not been processed.
            self.isValid = False
            self.errors.append('Parser: cannot process line "%s"' % line)


    def _resolveModel(self):

        def _resolveSimpleType(name):
            """ Search the name in enumeration of basic type or register it.
            """
            if name in self.model.enumerations:
                return self.model.enumerations[name]
            elif name in self.model.basicTypes:
                return self.model.basicTypes[name]
            else:
                self.model.basicTypes[name] = BasicType(name)
                return self.model.basicTypes[name]

        def _resolveClassType(name):
            """ Search in class names or association class names.
            """
            if name in self.model.classes:
                return self.model.classes[name]
            else:
                return self.model.associationClasses[name]

        def _resolveAttribute(attribute):
            # Resolve the attribute type
            attribute.type = _resolveSimpleType(attribute.type)

        def _resolveOperation(operation):
            # TODO: implement parsing of parameters and result type
            raise NotImplementedError('operation resolution not implemented')

        def _resolveClass(class_):
            # resolve superclasses
            class_.superclasses = \
                [_resolveClassType(name) for name in class_.superclasses]
            # resolve class attributes
            for a in class_.attributes.values():
                _resolveAttribute(a)
            # resolve class operations
            for op in class_.operations:
                pass # TODO

        def _resolveSubsets(role):
            # TODO: implement subsets role search
            raise NotImplementedError('subset resolution not implemented')

        def _resolveRole(role):
            # resolve role type
            role.type = _resolveClassType(role.type)
            # resolve qualifier types
            if role.qualifiers is not None:
                qs = role.qualifiers
                role.qualifiers = []
                for (n,t) in qs:
                    role.qualifiers.append((n,_resolveSimpleType(t)))
            if role.subsets is not None:
                for s in role.subsets:
                    pass # TODO _resolveSubset(role)
            if role.association.isBinary:
                rs = role.association.roles.values()
                role.opposite = rs[1] if role is rs[0] else rs[0]

        def _resolveAssociation(association):
            association.arity = len(association.roles)
            association.isBinary = (association.arity == 2)
            for role in association.roles.values():
                _resolveRole(role)

        def _resolveInvariant(invariant):
            c = _resolveClassType(invariant.class_)
            invariant.class_ = c
            c.invariants[invariant.name] = invariant

        # resolve class (and class part of class associations)
        cs = self.model.classes.values() \
            + self.model.associationClasses.values()
        for c in cs:
            _resolveClass(c)

        # resolve association (and association part of class association)
        as_ = self.model.associations.values() \
             + self.model.associationClasses.values()
        for a in as_:
            _resolveAssociation(a)

        # resolve invariant
        for i in self.model.invariants:
            _resolveInvariant(i)


# execute tests if launched from command line
if __name__ == "__main__":
    test_files = [
        'testch.use',
        'testch-err.use',
        'testch-1.use',
        'AssociationClass.use',
        'Demo.use',
        'Employee.use',
        'NestedOperationCalls.use',
        'Graph.use',
        'civstat.use',
        'tollcoll.use',
        'train.use',
        'actionsemantics.use',
        'OCL2MM.use',
        'UML13All.use',
        'UML13Core.use',
        'UML2MM.use',
        'CarRental2.use',
        'Empty.use',
        'Grammar.use',
        'derived.use',
        'Job.use',
        'Lists.use',
        'Math.use',
        'MultipleInheritance.use',
        'MultipleInheritance_unrelated.use',
        'Person.use',
        'Polygon.use',
        'Project.use',
        'RecursiveOperations.use',
        'redefines.use',
        'ReflexiveAssociation.use',
        'Student.use',
        'simpleSubset.use',
        'simpleSubsetUnion.use',
        'subsetsTest.use',
        'twoSubsets.use',
        'Sudoku.use',
        'Test1.use',
        'Tree.use',
        'CarRental.use',
        'RoyalAndLoyal.use',
        'OCLmetamodel.use',
        'EmployeeExtended.use',
        'bart.use',
    ]

    test_cases_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'tests', 'testcases')
    test_dir_2 = test_cases_dir + os.sep + 'use_tests'
    test_files2 = ['use_tests'+os.sep+f
                        for f in os.listdir(test_dir_2) if f.endswith('.use')]

    for test_file in test_files2  + test_files:
        print '-' * 10 + ' Parsing %s\n\n' % test_file
        use = UseOCLSpecification(test_cases_dir + os.sep + test_file)
        if use.isValid:
            print use.model
        else:
            print >> sys.stderr, 'Failed to create canonical form'
            for error in use.errors:
                print >> sys.stderr, error
                # UseOCLConverter.convertCanOCLInvariants(use.canonical_lines)

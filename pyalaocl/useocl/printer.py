# coding=utf-8

"""
Generate a USE OCL specification from a modeL.
This is currently only a preliminary version.
"""

#TODO: to be continued

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

class UseOCLPrinter(object):
    def __init__(self, model):
        self.theModel = model
        self.output = ''


    def do(self):
        self.output = ''
        self.model(self.theModel)
        return self.output


    def out(self, s):
        self.output += s


    def model(self, model):
        self.out('model %s\n\n' % model.name)

        for e in model.enumerations.values():
            self.enumeration(e)

        for c in model.classes.values():
            self.class_(c)

        for a in model.associations.values():
            self.association(a)

        for ac in model.associationClasses.values():
            self.associationClass(ac)


    def enumeration(self, enumeration):
        literals = ','.join(enumeration.literals)
        self.out( 'enum { %s };\n' % literals )


    def class_(self, class_):
        if class_.superclasses:
            sc = '< '+','.join(map(lambda s:s.name, class_.superclasses))
        else:
            sc = ''
        self.out("class %s %s\n" % (class_.name, sc))

        if class_.attributes:
            self.out('attributes\n')
            for attribute in class_.attributes.values():
                self.attribute(attribute)

        if class_.operations:
            self.out('operations\n')
            for operation in class_.operations.values():
                self.operation(operation)

        if class_.invariants:
            for invariant in class_.invariants.values():
                self.invariant(invariant)

        self.out('end\n\n')


    def association(self, association):
        self.out('%s %s between\n' % (association.kind, association.name))
        for role in association.roles.values():
            self.role(role)
        self.out('end\n\n')


    def associationClass(self, associationClass):
        if associationClass.superclasses:
            sc = ' < ' + ','.join(associationClass.superclasses.values())
        else:
            sc = ''
        self.out('associationclass %s%s between\n'
                 % (associationClass.name, sc))

        for role in associationClass.roles.values():
            self.role(role)

        if associationClass.attributes:
            self.out('attributes\n')
            for attribute in associationClass.attributes.values():
                self.attribute(attribute)

        if associationClass.operations:
            self.out('operations\n')
            for operation in associationClass.operations.values():
                self.operation(operation)

        self.out('end\n\n')


    def attribute(self, attribute):
        self.out('    %s : %s\n' % (attribute.name, attribute.type))


    def operation(self, operation):
        self.out('    %s\n' % operation.signature)
        # TODO - to be continued


    def invariant(self, invariant):
        pass


    def role(self, role):
        if role.name:
            rn = 'role '+role.name
        else:
            rn = ''
        max = '*' if role.cardinalityMax is None else role.cardinalityMax
        self.out('    %s[%s..%s] %s\n'
                 % (role.type.name, role.cardinalityMin, max, rn ))



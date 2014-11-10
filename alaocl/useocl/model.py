from collections import OrderedDict
import abc


class SourceElement(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, name, code=None):
        self.name = name
        self.source = code


class Model(SourceElement):
    def __init__(self, name, code=None):
        super(Model,self).__init__(name,code)
        self.isResolved = False

        self.enumerations = OrderedDict()
        self.classes = OrderedDict()
        self.associations = OrderedDict()
        self.associationClasses = OrderedDict()

        # indexed by operation full signatures.
        # e.g. 'Person::raiseSalary(rate : Real) : Real
        # This is useful for pre/post condition lookup
        self.operations = OrderedDict()

        self.invariants = []
        self.operationConditions = []

        # populated during the resolution phase
        self.basicTypes = OrderedDict()

    def __str__(self):
        return \
            'model '+self.name+'\n' \
            + 'enumerations        :' \
            + ','.join(self.enumerations.keys()) + '\n' \
            + 'classes             :' \
            + ','.join(self.classes.keys()) + '\n' \
            + 'associations        :' \
            + ','.join(self.associations.keys()) + '\n' \
            + 'association classes :' \
            + ','.join(self.associationClasses.keys()) + '\n' \
            + 'operations          :' \
            + ','.join(self.operations.keys()) + '\n' \
            + 'invariants          :' \
            + ','.join([i.name for i in self.invariants]) + '\n' \
            + 'operation conditions:' \
            + ','.join([i.name for i in self.operationConditions]) + '\n' \
            + 'basic types         :' \
            + ','.join(self.basicTypes.keys()) + '\n'

class TopLevelElement(SourceElement):
    __metaclass__ = abc.ABCMeta
    def __init__(self, name, model, code=None):
        super(TopLevelElement,self).__init__(name,code=code)
        self.model = model


class SimpleType(object):
    # not in the source, but used after symbol resolution
    __metaclass__ = abc.ABCMeta

class BasicType(SimpleType):
    # not in sources, but used created during symbol resolution
    def __init__(self, name):
        self.name = name

class Enumeration(TopLevelElement,SimpleType):
    def __init__(self, name, model, code=None, literals=()):
        super(Enumeration, self).__init__(name, model, code)
        self.model.enumerations[name] = self
        self.literals = literals


class Class(TopLevelElement):
    def __init__(self, name, model, isAbstract=False, superclasses=()):
        super(Class, self).__init__(name, model)
        self.model.classes[name] = self
        self.isAbstract = isAbstract
        self.superclasses = superclasses  # strings resolved as classes
        self.attributes = OrderedDict()
        self.operations = OrderedDict()
        self.invariants = OrderedDict()   # after resolution


class Attribute(SourceElement):
    def __init__(self, name, class_, code=None, type=None):
        super(Attribute, self).__init__(name, code=code)
        self.class_ = class_
        self.class_.attributes[name] = self
        self.type = type # string resolved as SimpleType



# class Parameter


class Operation(TopLevelElement):
    def __init__(self, name, model, class_, signature, code=None,
                 expression=None):
        super(Operation, self).__init__(name, model, code)
        self.class_ = class_
        self.class_.operations[name] = self
        self.signature = signature
        self.full_signature = '%s::%s' % (class_.name,self.signature)
        self.model.operations[self.full_signature] = self
        # self.parameters = parameters
        # self.return_type = return_type
        self.expression = expression

        self.conditions = OrderedDict()


class OperationCondition(TopLevelElement):
    __metaclass__ = abc.ABCMeta
    def __init__(self, name, model, operation, expression, code=None ):
        super(OperationCondition, self).__init__(name, model, code=code)
        self.model.operationConditions.append(self)
        operation.conditions[name] = self
        self.expression = expression


class PreCondition(OperationCondition):
    def __init__(self, name, model, operation, expression, code=None ):
        super(PreCondition, self).__init__(
            name, model, operation, expression, code=code)


class PostCondition(OperationCondition):
    def __init__(self, name, model, operation, expression, code=None):
        super(PostCondition, self).__init__(
            name, model, operation, expression, code=code)


class Invariant(TopLevelElement):
    def __init__(self, name, model, class_=None, code=None,
                 variable='self', expression=None,
                 additionalVariables = (),
                 isExistential=False):
        super(Invariant, self).__init__(name, model, code=code)
        self.model.invariants.append(self)
        self.class_ = class_  # str resolved in Class
        self.expression = expression
        self.variable = variable
        self.additionalVariables = additionalVariables
        self.isExistential = isExistential

    def __str__(self):
        return self.name

class Association(TopLevelElement):
    def __init__(self, name, model, kind=None):
        super(Association, self).__init__(name,model)
        self.model.associations[name] = self
        self.kind = kind
        self.roles = OrderedDict()
        self.arity = 0   # to be set
        self.isBinary = None # to be set


class Role(SourceElement):
    def __init__(self, name, association, code=None,
                 cardMin=None, cardMax=None, type=None, isOrdered=False,
                 qualifiers=None, subsets=None, isUnion=False,
                 expression=None):
        super(Role, self).__init__(name, code=code)
        self.association = association
        self.association.roles[name] = self
        self.cardinalityMin = cardMin
        self.cardinalityMax = cardMax
        self.type = type        # string to be resolved in Class
        self.isOrdered = isOrdered

        # (str,str) to be resolved in (str,SimpleType)
        self.qualifiers = qualifiers
        self.subsets = subsets
        self.isUnion = isUnion
        self.expression = expression
        self.opposite = None   # set for binary association only


class AssociationClass(Class,Association):
    def __init__(self, name, model, isAbstract=False, superclasses=()):
        # Use multi-inheritance to initialize the association class
        Class.__init__(self, name, model, isAbstract, superclasses)
        Association.__init__(self, name, model, 'associationclass' )
        # But register the association class apart and only once, to avoid
        # confusion and the duplicate in the associations and classes lists
        del self.model.classes[name]
        del self.model.associations[name]
        self.model.associationClasses[name] = self

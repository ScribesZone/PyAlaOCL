# coding=utf-8

"""
Result of the evaluation of a USE OCL state against a USE OCL model.
"""

from collections import OrderedDict
from abc import ABCMeta, abstractmethod

class ModelEvaluation(object):
    __metaclass__ = ABCMeta
    """
    Result of the evaluation of a USE OCL state against a USE OCL model.
    This could either be a ModelValidation if the state is valid,
    or a ModelViolation otherwise.
    """
    def __init__(self, model, state):
        self.model = model
        self.state = state
        self.isValidated = None  # abstract attribute. Filled by subclasses.



class ModelValidation(ModelEvaluation):
    """
    Result of the positive evaluation of a USE OCL state against a USE OCL
    model. Nothing particular to be stored.
    """
    def __init__(self, model, state):
        ModelEvaluation.__init__(self, model, state)
        self.isValidated = True


    def __str__(self):
        return 'Model validated'



class ModelViolation(ModelEvaluation):
    """
    Result of the negative evaluation of a USE OCL state agains a USE OCL
    model. Store invariants violations and/or cardinality violations.
    """
    def __init__(self, model, state):
        ModelEvaluation.__init__(self, model, state)
        self.isValidated = True

        self.invariantViolations = OrderedDict()
        """ dict(Invariant, InvariantViolation) """

        self.cardinalityViolations = OrderedDict()
        """ dict(Role, [CardinalityViolation] ) """


    def __str__(self):
        _ = 'Model not validated.'
        if len(self.invariantViolations) != 0:
            _ += ' %s invariant violated.' % len(self.invariantViolations)
        if len(self.cardinalityViolations) != 0:
            _ += ' %s cardinality violations' % len(self.cardinalityViolations)
        return _



class InvariantViolation(object):
    """
    Invariant violation.

    Looks like this in USE OCL::

        checking invariant (NUM) `CLASS::INVARIANT': FAILED.
          -> false : Boolean
        Instances of CLASS violating the invariant:
          -> Set{@bedroom201,@bedroom202, ...} : Set(Bedroom)
    """
    def __init__(self, modelViolation, invariant, violatingObjects):
        self.modelViolation = modelViolation
        modelViolation.invariantViolations[invariant] = self

        self.invariant = invariant
        self.violatingObjects = violatingObjects



class CardinalityViolation(object):
    """
    Cardinality violation.

    Looks like this in USE OCL::

        Multiplicity constraint violation in association `ASSOC':
          Object `OBJECT' of class `CLASS' is connected to NUM objects of class `CLASS'
          at association end `END' but the multiplicity is specified as `NUM'.
    """
    def __init__(self, modelViolation, role,
                 violatingObject, cardinalityFound):
        self.modelViolation = modelViolation
        if role not in modelViolation.cardinalityViolations:
            modelViolation.cardinalityViolations[role] = []
        modelViolation.cardinalityViolations[role].append(self)

        self.role = role
        self.violatingObject = violatingObject
        self.cardinalityFound = cardinalityFound



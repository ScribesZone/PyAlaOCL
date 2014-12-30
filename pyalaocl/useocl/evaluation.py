# coding=utf-8

from collections import OrderedDict
from abc import ABCMeta, abstractmethod

class ModelEvaluation(object):
    __metaclass__ = ABCMeta
    def __init__(self, model, state):
        self.model = model
        self.state = state
        self.isValidated = None



class ModelValidation(ModelEvaluation):
    def __init__(self, model, state):
        ModelEvaluation.__init__(self, model, state)
        self.isValidated = True


    def __str__(self):
        return 'Model validated'


class ModelViolation(ModelEvaluation):
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
    def __init__(self, modelViolation, invariant, violatingObjects):
        self.modelViolation = modelViolation
        modelViolation.invariantViolations[invariant] = self

        self.invariant = invariant
        self.violatingObjects = violatingObjects



class CardinalityViolation(object):
    def __init__(self, modelViolation, role,
                 violatingObject, cardinalityFound):
        self.modelViolation = modelViolation
        if role not in modelViolation.cardinalityViolations:
            modelViolation.cardinalityViolations[role] = []
        modelViolation.cardinalityViolations[role].append(self)

        self.role = role
        self.violatingObject = violatingObject
        self.cardinalityFound = cardinalityFound



# coding=utf-8

"""
Support for testing USE OCL specifications.
"""

import re
from collections import OrderedDict

import pyalaocl.useocl.model
import pyalaocl.useocl.evaluator











class UseEvaluationAndAssertionResults(
            pyalaocl.useocl.evaluator.UseEvaluationResults):
    """
    Extend the UseEvaluationResults by taking into account the potential
    assertions that may exist in each state file.
    """

    def __init__(self, useOCLModel, stateFiles):
        # build the results as usual
        pyalaocl.useocl.evaluator.UseEvaluationResults.__init__(
            self, useOCLModel, stateFiles
        )

        # TODO add here the list of all defined variables including None
        self.assertionEvaluationsMap = OrderedDict()
        """ dict(str,dict(Invariant,InvariantAssertionEvaluation)) """

        if self.wasExecutionValid:
            for state_file in self.stateFiles:
                self.__evaluateAssertionsForState(state_file)


    def __evaluateAssertionsForState(self, stateFile):
        self.assertionEvaluationsMap[stateFile] = OrderedDict()
        model = self.useOCLModel.model
        for assertion in _extractAssertionsFromFile(model, stateFile):
            inv = assertion.invariant
            modelEvaluation = self.modelEvaluationMap[stateFile]
            invEvaluation = modelEvaluation.invariantEvaluations[inv]
            ae = InvariantAssertionEvaluation(assertion, invEvaluation. isOK)
            self.assertionEvaluationsMap[stateFile][inv] = ae


class InvariantAssertionEvaluation(object):


    def __init__(self, invariantAssertion, actualResult):
        self.assertion = invariantAssertion

        self.actualResult = actualResult
        self.isOK = actualResult == self.assertion.expectedResult

    def __repr__(self):
        return 'Assert(%s=%s,%s)' % (
            self.assertion.invariant,
            self.assertion.expectedResult,
            "OK" if self.isOK else "KO"
        )


class InvariantAssertion(object):
    def __init__(self, invariant, expectedResult):
        self.invariant = invariant
        """ pyalaocl.useocl.model.Invariant """

        self.expectedResult = expectedResult
        """ bool """

    def __repr__(self):
        return 'Assert(%s,%s)' %(self.invariant,self.expectedResult)


def _extractAssertionsFromFile(useModel, soilFile):
    """
    Extract assertions objects from a soil file and a given model.
    :param useModel: the  model to which the soil file may reference
    :type useModel: pyalaocl.useocl.model.Model
    :param soilFile: path to the soil file
    :type soilFile: str
    :return: list of InvariantAssertion
    :rtype: [pyalaocl.useocl.model.Invariant]

    """
    _ = []
    triples = _extractAssertionStringsFromFile(soilFile)
    for (class_name, inv_name, result) in triples:
        try:
            # TODO: improve to support None as class name
            inv = useModel.findInvariant(class_name, inv_name)
        except:
            raise Exception('error with assertion in %s: %s::%s not found' %
                            (soilFile, class_name, inv_name))
        else:
            _.append(InvariantAssertion(inv,result))
    return _


def _extractAssertionStringsFromFile(soilFile):
    """
    Extract the assertion statement from a soil file.
    Returns a list of triplet with
    - the class name (optional),
    - the short name of invariant,
    - the expected result as a boolean
    """
    def _asBoolean(s):
        return {'ok':True, 'ko':False,'failed':False}[s.lower()]

    with open(soilFile) as f:
        text = f.read()
    regexp = r'--\ *@\s*(?:assert|validate)\s+' \
             r'(?:(\w+)[:_][:_])?(\w+)\s+' \
             r'(OK|KO|Failed)'
    triples = re.findall( regexp, text, re.IGNORECASE)
    return [(class_,inv,_asBoolean(result)) for (class_,inv,result) in triples]






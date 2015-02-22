# coding=utf-8


"""
Add support for "assertions" in USE OCL.
Assertions can be added in soil files in the form of comment like the
following::

    -- @assert MyClass::MyInvariant1 OK
    -- @assert MyClass::MyInvariant2 Failed
    -- @assert MyClass::MyInvariant6 OK

    ... the rest of the soil file ...

The "tester" engine will extract any assertion in the soil file and check
if the expected results are conform to what USE OCL interpreter return.
This module is to be used with the tester module.
"""

import re


class InvariantAssertionEvaluation(object):
    """
    The evaluation of an InvariantAssertion against a model if thr
    assertion is correct. If the assertion is incorrect then the evaluation
    is a failure. The status can therefore have three values:

    - 'OK': the assertion is correct and it evaluate to the expected result,
    - 'KO': the assertion is correct and it evaluate to a unepected result,
    - 'Failure': the assertion is incorrect
    """

    def __init__(self, invariantAssertion, actualResult):
        self.assertion = invariantAssertion
        if self.assertion.isCorrect:
            if actualResult == self.assertion.expectedResult:
                status = 'OK'
            else:
                status = 'KO'
        else:
            status = 'Failure'
        self.actualResult = actualResult
        self.status = status

    def __repr__(self):
        if self.status == 'Failure':
            return 'Assert(%s,%s)' % (
                self.assertion,
                self.status
            )
        else:
            return 'Assert(%s=%s,%s)' % (
                self.assertion.invariant,
                self.assertion.expectedResult,
                self.status
            )


class InvariantAssertion(object):
    """
    An InvariantAssertion bound to an invariant of a given model or
    an invalid InvariantAssertion if the invariant cannot be found.
    Just indicates what is the expected result for this invariant.
    """
    def __init__(self, useModel, stateFile,
                 className, invariantName, expectedResult):
        self.stateFile = stateFile
        self.className = className
        self.invariantName = invariantName
        self.useModel = useModel
        try:
            # TODO: improve to support None as class name
            self.invariant = useModel.findInvariant(className, invariantName)
        except:
            self.invariant = None
        self.isCorrect = self.invariant is not None
        """ bool """

        self.expectedResult = expectedResult
        """ bool """


    def __repr__(self):
        if self.isCorrect:
            return 'Assert(%s,%s)' % (self.invariant, self.expectedResult)
        else:
            return ('Assert(INCORRECT:%s::%s,%s)'
                % (self.className, self.invariantName, self.expectedResult))



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
        ia=InvariantAssertion(useModel, soilFile, class_name, inv_name, result)
        _.append(ia)
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
        return {'ok': True, 'ko': False, 'failed': False}[s.lower()]

    with open(soilFile) as f:
        text = f.read()
    regexp = r'--\ *@\s*(?:assert|validate)\s+' \
             r'(?:(\w+)[:_][:_])?(\w+)\s+' \
             r'(OK|KO|Failed)'
    triples = re.findall(regexp, text, re.IGNORECASE)
    return [(class_, inv, _asBoolean(result)) for (class_, inv, result) in
            triples]




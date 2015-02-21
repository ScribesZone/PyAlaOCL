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
    The evaluation of an InvariantAssertion agains a model.
    Could be OK if the result is the one expected or KO if this is not the
    case.
    """
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
    """
    An InvariantAssertion bound to an invariant of a given model.
    Just indicates what is the expected result for this invariant.
    """
    def __init__(self, stateFile, invariant, expectedResult):
        self.stateFile = stateFile
        self.invariant = invariant
        """ pyalaocl.useocl.model.Invariant """

        self.expectedResult = expectedResult
        """ bool """

    def __repr__(self):
        return 'Assert(%s,%s)' % (self.invariant, self.expectedResult)


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
            _.append(InvariantAssertion(soilFile, inv, result))
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




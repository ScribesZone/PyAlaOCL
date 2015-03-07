# coding=utf-8

from nose.tools import eq_, ok_
from collections import OrderedDict


class DataTestCase(object):
    def __init__(self, case):
        self._case = case
        self._id = self._case['id']
        self.caseSetup()

    def caseSetup(self):
        pass

    def checkPointValue(self, point):
        testLabel = '###%s#%s' % (point, self._id)
        expected = self._case[point]
        method = getattr(self, '_'+point)
        actual = method()
        print '    %s Expected:%s Actual:%s' % (testLabel,expected,actual)
        eq_(expected, actual, testLabel)

    def points(self):
        return []

    def checkAllPointValues(self):
        for point in self.points():
            self.checkPointValue(point)



class DataTestSuite(object):
    dataClass = None

    def test_generator(self):
        cases = self.getCases()
        for case in cases:
            print 'Creating %s(%s,...)' % (self.dataClass.__name__, id)
            dataTestCase = self.dataClass(case)
            fun = lambda: dataTestCase.checkAllPointValues()
            yield fun

    def getCases(self):
        if hasattr(self,'cases'):
            return self.cases
        else:
            return []



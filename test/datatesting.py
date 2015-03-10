# coding=utf-8

from nose.tools import eq_, ok_
from collections import OrderedDict



class DataTestCase(object):
    def __init__(self, case):
        self._ = None
        self._case = case
        self._id = self._case['id']
        self.caseSetup()
        if self._ is None:
            raise NotImplementedError(
                'Subclasses of DataTestCase must set _ in caseSetup')

    def caseSetup(self):
        pass

    def checkPointValue(self, point):
        testLabel = '###%s#%s' % (point, self._id)
        actual = self.evaluatePoint(point)
        expected = self.getExpected(point)
        if expected == 'XXX':
            print '    DEF   %s: found %s ' % (testLabel, actual)
        else:
            if expected == actual:
                print '    OK    %s: same %s ' % (testLabel,expected)
            else:
                print '    ERROR %s:' % testLabel
                print ' '*10+'Expected: %s' % expected
                print ' '*10+'Actual:   %s' % actual
            eq_(expected, actual, testLabel)

    def getExpected(self, point):
        if ((point not in self._case or self._case[point] == 'XXX')
            or ('XXX'in self._case)):
            return 'XXX'
        else:
            return self._case[point]

    def evaluatePoint(self, point):
        # (1) try to see if there is a method with the name _point on the
        # data class
        if hasattr(self, '_' + point):
            method = getattr(self, '_' + point)
            if method.im_self is not None:
                actual = method()
                return actual
        # (2) check to see if there is something with this name on the
        # object _
        if hasattr(self._, point):
            value = getattr(self._, point)
            if hasattr(value,'im_self') and value.im_self is not None:
                # This is a method, call it
                return value()
            else:
                # This is most probably not a method but an attribute
                return value
        raise Exception('ERROR IN TEST: No value on _ for field %s' % point)

    def points(self):
        raise NotImplementedError(
            'DataTestCase subclass must implement points()')

    def checkAllPointValues(self):
        for point in self.points():
            self.checkPointValue(point)



class DataTestSuite(object):
    DataTest = None

    def test_generator(self):
        cases = self.getCases()
        for case in cases:
            print 'Creating DataTest("%s")' % (case['id'])
            dataTestCase = self.DataTest(case)
            fun = lambda: dataTestCase.checkAllPointValues()
            yield fun

    def getCases(self):
        if hasattr(self,'cases'):
            return self.cases
        else:
            return []



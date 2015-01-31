# coding=utf-8

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.'+__name__)

from test.pyalaocl.useocl import TEST_CASES_DIRECTORY

import os
import pyalaocl.useocl.analyzer
from nose.plugins.attrib import attr



def test_UseOclModel_Simple():
    check_isValid('Demo.use')


@attr('slow')
def testGenerator_UseOclModel_full():
    test_files = [
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

    test_dir_2 = TEST_CASES_DIRECTORY + os.sep + 'use'
    test_files2 = ['use' + os.sep + f
                   for f in os.listdir(test_dir_2) if f.endswith('.use')]
    all_test_files = test_files2 + test_files

    for test_file in all_test_files:
        yield check_isValid, test_file


def check_isValid(testFile):
    useModel = pyalaocl.useocl.analyzer.UseOCLModel(
        TEST_CASES_DIRECTORY + os.sep + testFile)
    if useModel.isValid:
        print useModel.model
    assert useModel.isValid
        #else:
    #    print >> sys.stderr, 'Failed to create canonical form'
    #    for error in use.errors:
    #        print >> sys.stderr, error
    #        # UseOCLConverter.convertCanOCLInvariants(use.canonicalLines)

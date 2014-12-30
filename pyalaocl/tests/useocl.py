# coding=utf-8

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)



import os
import sys
import pyalaocl.useocl.analyzer

TEST_CASES_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'testcases')


def testUseOclModel():
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

    test_dir_2 = TEST_CASES_DIRECTORY + os.sep + 'use_tests'
    test_files2 = ['use_tests' + os.sep + f
                   for f in os.listdir(test_dir_2) if f.endswith('.use')]
    all_test_files = test_files2 + test_files
    print ('Starting %s tests',len(all_test_files))
    for test_file in all_test_files[0:-1]:
        print '-' * 10 + ' Parsing %s\n\n' % test_file
        use = pyalaocl.useocl.analyzer.UseOCLModel(
                    TEST_CASES_DIRECTORY + os.sep + test_file)
        if use.isValid:
            print use.model
        else:
            print >> sys.stderr, 'Failed to create canonical form'
            for error in use.errors:
                print >> sys.stderr, error
                # UseOCLConverter.convertCanOCLInvariants(use.canonicalLines)

# execute tests if launched from command line
if __name__ == "__main__":
    testUseOclModel()

# coding=utf-8
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from test.pyalaocl.useocl import getSoilFile, getUseFile, getZipFile

import os
import pyalaocl.useocl.tester
import pyalaocl.useocl.analyzer







def testGenerator_UseEvaluationAndAssertionResults():
    test_cases = [
        {'modelFile': 'Demo.use',
         'states': ['Demo1.soil', 'Demo2.soil', 'Demo3.soil', 'Demo4.soil'],
         'asserts': [
             """[Assert(Department::MoreEmployeesThanProjects=True,OK), Assert(Employee::MoreProjectsHigherSalary=True,OK), Assert(Project::BudgetWithinDepartmentBudget=False,KO), Assert(Project::EmployeesInControllingDepartment=False,KO)]
""",
            """[Assert(Department::MoreEmployeesThanProjects=True,OK), Assert(Employee::MoreProjectsHigherSalary=True,OK), Assert(Project::BudgetWithinDepartmentBudget=True,OK), Assert(Project::EmployeesInControllingDepartment=True,OK)]
""",
            """[Assert(Department::MoreEmployeesThanProjects=True,OK), Assert(Employee::MoreProjectsHigherSalary=True,OK), Assert(Project::BudgetWithinDepartmentBudget=False,OK), Assert(Project::EmployeesInControllingDepartment=True,KO)]
""",
            """[Assert(Department::MoreEmployeesThanProjects=True,OK), Assert(Employee::MoreProjectsHigherSalary=True,OK), Assert(Project::BudgetWithinDepartmentBudget=True,OK), Assert(Project::EmployeesInControllingDepartment=True,OK)]
""",    ],
         'failures': """[Assert(Project::BudgetWithinDepartmentBudget=False,KO), Assert(Project::EmployeesInControllingDepartment=False,KO), Assert(Project::EmployeesInControllingDepartment=True,KO)]"""

      }
    ]

    for test_case in test_cases:
        test_name = test_case['modelFile']
        check_UseEvaluationAndAssertionResults.description = test_name
        yield check_UseEvaluationAndAssertionResults, test_case


def check_UseEvaluationAndAssertionResults(testCase):
    # get the model parsed
    useFile = getUseFile(testCase['modelFile'])
    useOCLModel = pyalaocl.useocl.analyzer.UseOCLModel(useFile)
    stateFiles = map(getSoilFile,testCase['states'])
    r = pyalaocl.useocl.tester.UseEvaluationAndAssertionResults(
        useOCLModel, stateFiles)

    assert (r.assertionEvaluationsByStateFile).keys() == stateFiles
    #assert repr(r.assertionEvaluationsByStateFile[stateFile]) == testCase['assert']
    # print r.assertionEvaluationsMap.values()
    for i, stateFile in enumerate(stateFiles):
        # print r.assertionEvaluationsMap[stateFile].values()
        assert repr(r.assertionEvaluationsByStateFile[stateFile]
                    == testCase['asserts'][i])

    assert repr(r.assertionViolations) == testCase['failures']
    assert r.nbOfAssertionViolations == 3
    assert r.hasViolatedAssertions == True
    assert r.nbOfAssertionEvaluations == 16





def testGenerator_ZipTestSuite():
    test_cases = [
        {'zip': 'Demo-G007.zip',
         'use': 1,
         'soil': 4,
         'violations': 3,
         'evaluation': 16,
        }
    ]

    for test_case in test_cases:
        test_name = test_case['zip']
        check_ZipTestSuite.description = test_name
        yield check_ZipTestSuite, test_case


def check_ZipTestSuite(case):
    # get the model parsed
    if case['zip'].startswith('http://'):
        zipFileId = case['zip']
    else:
        zipFileId = getZipFile(case['zip'])
    ts = pyalaocl.useocl.tester.ZipTestSuite(zipFileId)
    assert len(ts.filesByExtension['.use']) == case['use']
    assert len(ts.filesByExtension['.soil']) == case['soil']
    assert ts.nbOfAssertionViolations == case['violations']
    assert ts.nbOfAssertionEvaluations == case['evaluation']


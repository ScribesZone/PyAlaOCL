# coding=utf-8
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from test.pyalaocl.useocl import getSoilFile, getUseFile

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

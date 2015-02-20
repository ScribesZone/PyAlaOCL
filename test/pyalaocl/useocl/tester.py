# coding=utf-8
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from test.pyalaocl.useocl import getSoilFile, getUseFile

import os
import pyalaocl.useocl.tester
import pyalaocl.useocl.analyzer




def testGenerator_extractAssertion():
    test_cases = [
        { 'modelFile': 'Demo.use',
          'states':  [
                {'state': 'Demo1.soil',
                'parsed': """[('Department', 'MoreEmployeesThanProjects', True), ('Employee', 'MoreProjectsHigherSalary', True), ('Project', 'BudgetWithinDepartmentBudget', False), ('Project', 'EmployeesInControllingDepartment', False)]""",
                'withInv':"""[Assert(Department::MoreEmployeesThanProjects,True), Assert(Employee::MoreProjectsHigherSalary,True), Assert(Project::BudgetWithinDepartmentBudget,False), Assert(Project::EmployeesInControllingDepartment,False)]"""
                },
                {'state': 'Demo2.soil',
                 'parsed': """[('Department', 'MoreEmployeesThanProjects', True), ('Employee', 'MoreProjectsHigherSalary', True), ('Project', 'BudgetWithinDepartmentBudget', True), ('Project', 'EmployeesInControllingDepartment', True)]""",
                'withInv':"""[Assert(Department::MoreEmployeesThanProjects,True), Assert(Employee::MoreProjectsHigherSalary,True), Assert(Project::BudgetWithinDepartmentBudget,True), Assert(Project::EmployeesInControllingDepartment,True)]""",
                },
                {'state': 'Demo3.soil',
                 'parsed': """[('Department', 'MoreEmployeesThanProjects', True), ('Employee', 'MoreProjectsHigherSalary', True), ('Project', 'BudgetWithinDepartmentBudget', False), ('Project', 'EmployeesInControllingDepartment', True)]""",
                 'withInv': """[Assert(Department::MoreEmployeesThanProjects,True), Assert(Employee::MoreProjectsHigherSalary,True), Assert(Project::BudgetWithinDepartmentBudget,False), Assert(Project::EmployeesInControllingDepartment,True)]"""
                },
                {'state': 'Demo4.soil',
                 'parsed': """[('Department', 'MoreEmployeesThanProjects', True), ('Employee', 'MoreProjectsHigherSalary', True), ('Project', 'BudgetWithinDepartmentBudget', True), ('Project', 'EmployeesInControllingDepartment', True)]""",
                 'withInv':"""[Assert(Department::MoreEmployeesThanProjects,True), Assert(Employee::MoreProjectsHigherSalary,True), Assert(Project::BudgetWithinDepartmentBudget,True), Assert(Project::EmployeesInControllingDepartment,True)]"""

    },
          ]
        }
    ]

    for test_case in test_cases:
        test_name = test_case['modelFile']
        check_extractAssertionStringsFromFile.description = test_name
        yield check_extractAssertionStringsFromFile, test_case

    for test_case in test_cases:
        test_name = test_case['modelFile']
        check_extractAssertionsFromFile.description = test_name
        yield check_extractAssertionsFromFile, test_case

def check_extractAssertionStringsFromFile(testCase):
    for state_case in testCase['states']:
        soilFile = getSoilFile(state_case['state'])
        _ = pyalaocl.useocl.tester._extractAssertionStringsFromFile(soilFile)
        # print 'test in ',soilFile
        # print repr(_)
        # print  state_case['parsed']
        assert repr(_) == state_case['parsed']

def check_extractAssertionsFromFile(testCase):
    # get the model parsed
    useFile = getUseFile(testCase['modelFile'])
    model = pyalaocl.useocl.analyzer.UseOCLModel(useFile).model

    for state_case in testCase['states']:
        soilFile = getSoilFile(state_case['state'])
        _ = pyalaocl.useocl.tester._extractAssertionsFromFile(model, soilFile)
        assert repr(_) == state_case['withInv']









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
""",    ]
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

    assert (r.assertionEvaluationsMap).keys() == stateFiles
    #assert repr(r.assertionEvaluationsMap.values()) == testCase['assert']
    # print r.assertionEvaluationsMap.values()
    for i, stateFile in enumerate(stateFiles):
        # print r.assertionEvaluationsMap[stateFile].values()
        assert repr(r.assertionEvaluationsMap[stateFile].values()
                    == testCase['asserts'][i])

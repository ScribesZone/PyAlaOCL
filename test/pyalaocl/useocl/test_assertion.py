# coding=utf-8
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from test.pyalaocl.useocl import getSoilFile, getUseFile

import pyalaocl.useocl.assertion
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
                {'state': 'DemoEmpty.soil',
                 'parsed': """[('Department', 'MoreEmployeesThanProjects', True)]""",
                 'withInv': """[Assert(Department::MoreEmployeesThanProjects,True)]""",
                },
                {'state': 'DemoIncorrectAssertions2.soil',
                 'parsed': """[('Department', 'MoreEmployeesThanProjects', True), ('ERROR', 'MoreProjectsHigherSalary', True), ('Project', 'ERROR', False), ('Project', 'EmployeesInControllingDepartment', False)]""",
                 'withInv': """[Assert(Department::MoreEmployeesThanProjects,True), Assert(INCORRECT:ERROR::MoreProjectsHigherSalary,True), Assert(INCORRECT:Project::ERROR,False), Assert(Project::EmployeesInControllingDepartment,False)]"""
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
        _ = pyalaocl.useocl.assertion._extractAssertionStringsFromFile(soilFile)
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
        _ = pyalaocl.useocl.assertion._extractAssertionsFromFile(model, soilFile)
        assert repr(_) == state_case['withInv']








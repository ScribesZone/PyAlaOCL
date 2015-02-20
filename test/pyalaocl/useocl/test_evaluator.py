# coding=utf-8
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from test.pyalaocl.useocl import TEST_CASES_DIRECTORY

import os
import pyalaocl.useocl.evaluator
import pyalaocl.useocl.analyzer


def testGenerator_UseEvaluationResults():
    test_cases_dir = TEST_CASES_DIRECTORY
    soil_dir = 'soil'
    test_cases = [
        {'model': 'Demo.use',
         'states': ['Demo1.soil', 'Demo2.soil', 'Demo3.soil', 'Demo4.soil'],
         'wasExecutionValid':True,
         'evaluationsRepr':"""[Violation(Demo1,INV(MoreEmployeesThanProjects=OK,MoreProjectsHigherSalary=OK,BudgetWithinDepartmentBudget=OK,EmployeesInControllingDepartment=OK),ROLE(WorksIn::department)), Violation(Demo2,INV(MoreEmployeesThanProjects=OK,MoreProjectsHigherSalary=OK,BudgetWithinDepartmentBudget=OK,EmployeesInControllingDepartment=OK),ROLE(WorksIn::department)), Violation(Demo3,INV(BudgetWithinDepartmentBudget=KO,EmployeesInControllingDepartment=KO,MoreEmployeesThanProjects=OK,MoreProjectsHigherSalary=OK),ROLE(Controls::department)), Valid(Demo4)]"""
         }
    ]

    for test_case in test_cases:
        #-- load the model from test_cases_dir
        model_file = \
            os.path.join(test_cases_dir, test_case['model'])
        use_model = pyalaocl.useocl.analyzer.UseOCLModel(model_file)
        assert use_model.isValid   # we assume that this is ok

        #-- get the state files from 'states'
        state_files = [
            os.path.join(test_cases_dir, soil_dir, soil_file)
            for soil_file in test_case['states']
        ]
        name = test_case['model']
        check_UseEvaluationResults.description = name
        yield check_UseEvaluationResults, use_model, state_files, test_case


def check_UseEvaluationResults(useModel, stateFiles, testCase):
    _ =  pyalaocl.useocl.evaluator.UseEvaluationResults(useModel, stateFiles)
    assert len(_.modelEvaluationMap) == len(stateFiles)
    assert _.wasExecutionValid == testCase['wasExecutionValid']
    # uncommend this line to see the details of the evaluations
    # print _
    #
    # print repr(_.modelEvaluationMap.values())
    # print testCase['evaluationsRepr']
    assert repr(_.modelEvaluationMap.values()) == testCase['evaluationsRepr']

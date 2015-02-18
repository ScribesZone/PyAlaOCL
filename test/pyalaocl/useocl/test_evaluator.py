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
         'states': ['Demo1.soil', 'Demo2.soil', 'Demo3.soil', 'Demo4.soil']}
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
        check_UseEvaluationResults.description = str(test_case)
        yield check_UseEvaluationResults, use_model, state_files


def check_UseEvaluationResults(useModel,stateFiles):
    validation_result = \
        pyalaocl.useocl.evaluator.UseEvaluationResults(useModel, stateFiles)
    print validation_result
    assert validation_result

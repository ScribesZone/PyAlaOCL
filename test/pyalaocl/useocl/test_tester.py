# coding=utf-8
"""
Test the tester
"""

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from test.pyalaocl.useocl import getSoilFile, getUseFile, getZipFile

import os
import pyalaocl.useocl.tester
import pyalaocl.useocl.analyzer







def XXXtestGenerator_UseEvaluationAndAssertionResults():
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
    ],

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

    print repr(r.assertionEvaluationsByStatus['KO'])
    print testCase['failures']
    assert repr(r.assertionEvaluationsByStatus['KO']) == testCase['failures']
    print
    assert r.nbOfAssertionViolations == 3
    assert r.hasAssertionViolations == True
    assert r.nbOfAssertionEvaluations == 16





def testGenerator_ZipTestSuite():
    root = r'C:\Dropbox\_JFE\ENSEIGNEMENT\M2R-1415\AEIS1415\CyberResidencesOCL\LIVRABLES\CyberResidencesOCL-3.0-'
    test_cases = [
        {'zip': 'Demo-G007.zip',
         'use': 1,
         'soil': 4,
         'violations': 3,
         'evaluation': 16,
        },
        # {'zip': 'https://github.com/megaplanet/PyAlaOCL/raw/master/test/pyalaocl/useocl/testcases/zip/Demo-G007.zip',
        # 'use': 1,
        # 'soil': 4,
        # 'violations': 3,
        # 'evaluation': 16,
        # },
        {'zip': root + 'G17.zip',
        'main': 'CyberResidencesOCL-3.0.use',
        'use': 2,
        'soil': 86,
        'violations': 3,
        'evaluation': 16,
        },
        # {'zip': root + 'G28.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 84,
        # 'violations': 3,
        # 'evaluation': 16,
        # },
        # {'zip': root + 'G50.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 84,
        # 'violations': 3,
        # 'evaluation': 16,
        # },
        #{'zip': root + 'G55.zip',
        #'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 4,
        # 'violations': 3,
        # 'evaluation': 16,
        # },
        # {'zip': root + 'G68.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 2,
        # 'soil': 172,
        # 'violations': 2,
        # 'evaluation': 172,
        # },
        # {'zip': root + 'G70.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 85,
        # 'violations': 1,
        # 'evaluation': 85,
        # },
        # {'zip': root + 'G78.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 84,
        # 'violations': 1,
        # 'evaluation': 84,
        # },
    ]

    for test_case in test_cases:
        test_name = test_case['zip']
        check_ZipTestSuite.description = test_name
        yield check_ZipTestSuite, test_case


def check_ZipTestSuite(case):
    # get the model parsed
    if 'main' in case:
        main = case['main']
    else:
        main = None
    if case['zip'].startswith('http') or case['zip'].startswith('ftp'):
        zipFileId = case['zip']
    else:
        zipFileId = getZipFile(case['zip'])
    ts = pyalaocl.useocl.tester.ZipTestSuite(zipFileId, useFileShortName=main)
    print len(ts.filesByExtension['.use'])
    print len(ts.filesByExtension['.soil'])
    assert len(ts.filesByExtension['.use'])  == case['use']
    assert len(ts.filesByExtension['.soil']) == case['soil']
    #assert ts.nbOfAssertionViolations == case['violations']
    #assert ts.nbOfAssertionEvaluations == case['evaluation']
    #ts.free()




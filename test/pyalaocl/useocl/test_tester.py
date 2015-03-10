# coding=utf-8
"""
Test the tester
"""

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from test.pyalaocl.useocl \
    import getSoilFile, getSoilFileList, getUseFile, getZipFile

import os
import pyalaocl.useocl.tester
import pyalaocl.useocl.analyzer

from test.datatesting import DataTestCase, DataTestSuite

class Test_UseEvaluationAndAssertionResult(DataTestSuite):
    class DataTest(DataTestCase):
        def caseSetup(self):
            self.modelFile = getUseFile(self._case['model'])
            self.useModel = pyalaocl.useocl.analyzer.UseOCLModel(
                self.modelFile)
            assert self.useModel.isValid  # we assume that this is ok
            self.stateFiles = getSoilFileList(self._case['states'])
            self._ = pyalaocl.useocl.tester.UseEvaluationAndAssertionResults(
                self.useModel, self.stateFiles)
            #print repr(self._.assertionEvaluationsByStatus['KO'])
            #print repr(self._.assertionEvaluationsByStateFile[stateFile])

        def points(self):return [
            'nbOfAssertionValidations',
            'nbOfAssertionViolations',
            'hasAssertionViolations',
            'nbOfAssertionFailures',
            'nbOfAssertionEvaluations',
            'allViolations',
            'allValidations',
            'allFailures',
        ]
        def _allValidations(self):
            return repr(self._.assertionEvaluationsByStatus['OK'])
        def _allViolations(self):
            return repr(self._.assertionEvaluationsByStatus['KO'])
        def _allFailures(self):
            return repr(self._.assertionEvaluationsByStatus['Failure'])
    cases = [
        {
            'id':'Demo.use',
            'model':'Demo.use',
            'states': ['Demo1.soil', 'Demo2.soil', 'Demo3.soil', 'Demo4.soil'],
            'nbOfAssertionValidations': 13,
            'nbOfAssertionViolations': 3,
            'hasAssertionViolations': True,
            'nbOfAssertionFailures': 0,
            'hasAssertionFailures' : False,
            'nbOfAssertionEvaluations': 16,
            'allViolations':"""[Assert(Project::BudgetWithinDepartmentBudget=False,KO), Assert(Project::EmployeesInControllingDepartment=False,KO), Assert(Project::EmployeesInControllingDepartment=True,KO)]""",
            'allValidations':"""[Assert(Department::MoreEmployeesThanProjects=True,OK), Assert(Employee::MoreProjectsHigherSalary=True,OK), Assert(Department::MoreEmployeesThanProjects=True,OK), Assert(Employee::MoreProjectsHigherSalary=True,OK), Assert(Project::BudgetWithinDepartmentBudget=True,OK), Assert(Project::EmployeesInControllingDepartment=True,OK), Assert(Department::MoreEmployeesThanProjects=True,OK), Assert(Employee::MoreProjectsHigherSalary=True,OK), Assert(Project::BudgetWithinDepartmentBudget=False,OK), Assert(Department::MoreEmployeesThanProjects=True,OK), Assert(Employee::MoreProjectsHigherSalary=True,OK), Assert(Project::BudgetWithinDepartmentBudget=True,OK), Assert(Project::EmployeesInControllingDepartment=True,OK)]""",
            'allFailures': """[]""",
        }
    ]





class Test_ZipTestSuite(DataTestSuite):
    root = r'C:\Dropbox\_JFE\ENSEIGNEMENT\M2R-1415\AEIS1415\CyberResidencesOCL\LIVRABLES\CyberResidencesOCL-3.0-'

    class DataTest(DataTestCase):
        def caseSetup(self):
            if 'main' in self._case:
                self.main = self._case['main']
            else:
                self.main = None
            self.zipFileId = getZipFile(self._case['zip'])
            self._ = pyalaocl.useocl.tester.ZipTestSuite(
                self.zipFileId,
                useFileShortName=self.main)

            print ".use",self._.filesByExtension['.use']
            print ".soil",self._.filesByExtension['.soil']
            #print len(ts.filesByExtension['.soil'])
            #assert len(ts.filesByExtension['.use']) == case['use']
            #assert len(ts.filesByExtension['.soil']) == case['soil']
            #assert ts.nbOfAssertionViolations == case['violations']
            #assert ts.nbOfAssertionEvaluations == case['evaluation']
            #ts.free()

        def points(self):  return [
            'soil',
            'use',
            'nbOfAssertionValidations',
            'nbOfAssertionViolations',
            'nbOfAssertionFailures',
            'nbOfAssertionEvaluations',
        ]

        def _soil(self):
            return len(self._.filesByExtension['.soil'])
        def _use(self):
            return len(self._.filesByExtension['.use'])


    cases = [
        # {'id': 'Demo-G007',
        #  'zip': 'Demo-G007.zip',
        #  'use': 1,
        #  'soil': 4,
        #  'nbOfAssertionValidations': 13,
        #  'nbOfAssertionViolations': 3,
        #  'nbOfAssertionFailures': 0,
        #  'nbOfAssertionEvaluations': 16,
        # },
        # { 'id': 'Demo-G007@github',
        # 'zip': 'https://github.com/megaplanet/PyAlaOCL/raw/master/test/pyalaocl/useocl/testcases/zip/Demo-G007.zip',
        # 'use': 1,
        # 'soil': 4,
        # 'nbOfAssertionValidations': 13,
        # 'nbOfAssertionViolations': 3,
        # 'nbOfAssertionFailures': 0,
        # 'nbOfAssertionEvaluations': 16,
        # },
        {'id': 'G17',
        'zip': root + 'G17.zip',
        'main': 'CyberResidencesOCL-3.0.use',
        'use': 2,
        'soil': 86,
        'nbOfAssertionValidations': 64,
        'nbOfAssertionViolations': 5,
        'nbOfAssertionFailures': 0,
        'nbOfAssertionEvaluations': 69,
        },
        # {
        # 'id': 'G28',
        # 'zip': root + 'G28.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 84,
        # 'nbOfAssertionValidations': 0,
        # 'nbOfAssertionViolations': 0,
        # 'nbOfAssertionFailures': 0,
        # 'nbOfAssertionEvaluations': 0,
        # },
        #
        # {
        # 'id': 'G50',
        # 'zip': root + 'G50.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 84,
        # 'nbOfAssertionValidations': 71,
        # 'nbOfAssertionViolations': 0,
        # 'nbOfAssertionFailures': 0,
        # 'nbOfAssertionEvaluations': 71,
        # },

        # {
        # 'id':'G55',
        # 'zip': root + 'G55.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 84,
        # 'nbOfAssertionValidations': 0,
        # 'nbOfAssertionViolations': 0,
        # 'nbOfAssertionFailures': 0,
        # 'nbOfAssertionEvaluations': 0,
        # },
        #
        # {
        # 'id':'G68', 'XXX': 'XXX',
        # 'zip': root + 'G68.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 86,
        # 'nbOfAssertionValidations': 0,
        # 'nbOfAssertionViolations': 0,
        # 'nbOfAssertionFailures': 0,
        # 'nbOfAssertionEvaluations': 64,
        # },

        # {
        # 'id':'G70',
        # 'zip': root + 'G70.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'nbOfAssertionValidations': 62,
        # 'nbOfAssertionViolations': 2,
        # 'nbOfAssertionFailures': 0,
        # 'nbOfAssertionEvaluations': 64,
        # },
        #
        # {
        # 'id':'G78',
        # 'zip': root + 'G78.zip',
        # 'main': 'CyberResidencesOCL-3.0.use',
        # 'use': 1,
        # 'soil': 84,
        # 'nbOfAssertionValidations': 82,
        # 'nbOfAssertionViolations': 1,
        # 'nbOfAssertionFailures': 0,
        # 'nbOfAssertionEvaluations': 83,
        # },
    ]






# coding=utf-8

"""
Support for testing USE OCL specifications. The
UseEvaluationAndAssertionResults class extends the UseEvaluationResults
with the evaluation and results of assertions in soil file.
This class also provide support for USE OCL TestSuite, in particular in the
form of zip files.
"""

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from collections import OrderedDict
import os.path

import pyalaocl.utils.zip
import pyalaocl.useocl.model
import pyalaocl.useocl.analyzer
import pyalaocl.useocl.evaluator
import pyalaocl.useocl.assertion
import pyalaocl.useocl.soil




class UseEvaluationAndAssertionResults(
            pyalaocl.useocl.evaluator.UseEvaluationResults):
    """
    Extend the UseEvaluationResults by taking into account the potential
    assertions that may exist in each state file.
    """

    def __init__(self, useOCLModel, stateFiles):
        # build the results as usual
        pyalaocl.useocl.evaluator.UseEvaluationResults.__init__(
            self, useOCLModel, stateFiles
        )

        self.assertionEvaluationsByStateFile = OrderedDict()
        """ dict(str,[InvariantAssertionEvaluation]) """

        self.assertionEvaluationsByStatus = OrderedDict()
        """ dict(str,[InvariantAssertionEvaluation]) """

        for status in ['OK', 'KO', 'Failure']:
            self.assertionEvaluationsByStatus[status] = []

        #--- evaluate all valid state files
        # (empty and erroneous files are skipped)
        if self.isCorrect:
            for state_file in self.stateFiles:
                self.__evaluateAssertionsFromState(state_file)

        self.nbOfAssertionValidations = \
            len(self.assertionEvaluationsByStatus['OK'])
        self.nbOfAssertionViolations = \
            len(self.assertionEvaluationsByStatus['KO'])
        self.hasAssertionViolations = self.nbOfAssertionViolations > 0
        self.nbOfAssertionFailures = \
            len(self.assertionEvaluationsByStatus['Failure'])
        self.hasAssertionFailures = self.nbOfAssertionFailures > 0
        self.nbOfAssertionEvaluations = \
            sum(map(len, self.assertionEvaluationsByStateFile.values()))


    def __evaluateAssertionsFromState(self, stateFile):
        """
        Evaluate the assertions contained in the given state file.
        Set assertionEvaluationsByStateFile[stateFile}
        as well as assertionEvaluationsByStatus.
        :param stateFile: the state file to process
        :type stateFile: str
        """
        log.debug('__evaluateAssertionsForState(%s)' % stateFile)
        self.assertionEvaluationsByStateFile[stateFile] = []
        for assertion in pyalaocl.useocl.assertion._extractAssertionsFromFile(
                self.useOCLModel.model, stateFile):
            self.__evaluateAssertion(assertion)


    def __evaluateAssertion(self, assertion):
        log.debug('--- __evaluateAssertion(%s)' % assertion)

        if assertion.isCorrect:
            # get the actual result from the invariant evaluation
            inv = assertion.invariant
            if assertion.stateFile not in self.modelEvaluationMap:
                print '###    ', assertion.stateFile
                print '### IS NOT IN'
                for e in self.modelEvaluationMap.keys():
                    pass # print "#      ",e
                print '### EMPTY STATE FILES: %s' % self.nbOfEmptyStateFiles
                for e in self.emptyStateFiles:
                    print "#      ", e
                print '### STATE FILES : %s' % len(self.stateFiles)
                print '### EVAL MAP: %s' % len(self.modelEvaluationMap.keys())
                print '$$$'
                with open(r'c:\tmp\output.txt','w') as f:
                    f.write(self.output_text)
            model_evaluation = self.modelEvaluationMap[assertion.stateFile]


            inv_evaluation = model_evaluation.invariantEvaluations[inv]
            actual_result = inv_evaluation.isOK
        else:
            # the assertion is not correct, so actual_result does not matter
            actual_result = None
        ae = pyalaocl.useocl.assertion.InvariantAssertionEvaluation(
            assertion, actual_result)
        # add the evaluation to the proper lists
        self.assertionEvaluationsByStateFile[assertion.stateFile].append(ae)
        self.assertionEvaluationsByStatus[ae.status].append(ae)




class TestSuite(UseEvaluationAndAssertionResults):
    __test__ = False   # To avoid being taken as a test by nose

    def __init__(self, useFile, stateFiles, testId=None):
        self.testId = testId
        self.useFile = useFile
        use_ocl_model = pyalaocl.useocl.analyzer.UseOCLModel(useFile)
        UseEvaluationAndAssertionResults.__init__(self, use_ocl_model,
                                                  stateFiles)




class ZipTestSuite(TestSuite, pyalaocl.utils.zip.ZipArtefact):
    """
    Test suite represented as a local or remote zip file
    The _compute methods can be overriden if needed to change the behavior
    of this class.
    """
    __test__ = False  # To avoid being taken as a test by nose

    def __init__(self, zipFileId, testId=None,
                 targetDirectory = None, filter=('.soil', '.use'),
                 useFileShortName = None):
        """
        Build a USE OCL test suite by extracting the .use file and .soil
        file from an archive.
        """
        self.useFileShortName = useFileShortName
        pyalaocl.utils.zip.ZipArtefact.__init__(
            self,
            zipFileId=zipFileId,
            targetDirectory=targetDirectory,
            filter=filter)
        TestSuite.__init__(
            self,
            useFile = self._computeUseFile(),
            stateFiles =list(self._computeStateFiles()),
            testId = self._computeTestId(testId))



    def _computeTestId(self, testId=None):
        """
        Compute the testId of the test. This function could be overridden
        if necessary.
        :param testId: The testId or none given as a parameter of the test
            constructor
        :type testId: str
        :return: The computed testId possibily based on the name or content
            of the archive.
        :rtype: str
        """
        return testId


    def _computeUseFile(self):
        """
        Return the name of the file corresponding "the" .use file.
        If useFileShortName is None, it is assumed that there is only one
        .use file in the zip. Otherwise take the .use file with the given name
        and generate an error if they are various such files.
        :return:
        :rtype:
        """
        if self.useFileShortName is None:
            files = self.filesByExtension['.use']
        else:
            files = [file for file in self.filesByExtension['.use']
                     if os.path.basename(file) == self.useFileShortName]
        if len(files) == 1:
            return files[0]
        else:
            raise Exception('More than one .use file: %s'  % files )


    def _computeStateFiles(self):
        """
        Select the state files form all the soil files in the archives.
        This function could be overriden.
        :return: a list of soil file that will serve as the state files
        :rtype: [str]
        """
        return list(self.filesByExtension['.soil'])



class CrossZipTestSuite(object):
    __test__ = False  # To avoid being taken as a test by nose
    def __init__(self, idsAndZips,
                 targetDirectory=None, extractOnly=('.soil', '.use')):
        for (id,zip) in idsAndZips:
            pass


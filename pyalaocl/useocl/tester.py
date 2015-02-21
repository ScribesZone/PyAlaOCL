# coding=utf-8

"""
Support for testing USE OCL specifications.
"""

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

from collections import OrderedDict

import pyalaocl.useocl.model
import pyalaocl.useocl.analyzer
import pyalaocl.useocl.evaluator
import pyalaocl.useocl.assertion




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

        self.assertionViolations = []
        """ [InvariantAssertionEvaluation] """


        if self.wasExecutionValid:
            for state_file in self.stateFiles:
                self.__evaluateAssertionsForState(state_file)

        self.__buildSummmary()

        self.nbOfAssertionViolations = len(self.assertionViolations)
        self.hasViolatedAssertions = self.nbOfAssertionViolations > 0
        self.nbOfAssertionEvaluations = \
            sum(map(len,self.assertionEvaluationsByStateFile.values()))

    def __evaluateAssertionsForState(self, stateFile):
        """
        Set assertionEvaluationsMap[stateFile} for the given file
        :param stateFile: the state file to process
        :type stateFile: str
        """
        self.assertionEvaluationsByStateFile[stateFile] = []
        model = self.useOCLModel.model
        for assertion in pyalaocl.useocl.assertion._extractAssertionsFromFile(
                model, stateFile):
            inv = assertion.invariant
            modelEvaluation = self.modelEvaluationMap[stateFile]
            invEvaluation = modelEvaluation.invariantEvaluations[inv]
            ae = pyalaocl.useocl.assertion.InvariantAssertionEvaluation(
                assertion, invEvaluation. isOK)
            self.assertionEvaluationsByStateFile[stateFile].append(ae)


    def __buildSummmary(self):
        self.assertionViolations = [
            ae
                for aes in self.assertionEvaluationsByStateFile.values()
                for ae in aes
                if not ae.isOK
        ]


class TestSuite(UseEvaluationAndAssertionResults):
    __test__ = False   # To avoid being taken as a test by nose

    def __init__(self, useFile, stateFiles, testId=None):
        self.testId = testId
        self.useFile = useFile
        use_ocl_model = pyalaocl.useocl.analyzer.UseOCLModel(useFile)
        UseEvaluationAndAssertionResults.__init__(self, use_ocl_model,
                                                  stateFiles)

import zipfile
import os.path
import tempfile
import urllib
import shutil


class ZipTestSuite(TestSuite):
    __test__ = False  # To avoid being taken as a test by nose

    def __init__(self, zipFileId, testId=None,
                 targetDirectory = None, extractOnly=('.soil', '.use')):
        self.zipFileId = zipFileId
        self.targetDirectory = targetDirectory
        self.extractOnly = extractOnly
        self.isZipRemote = None                # computed in _computeZipFile
        self.zipFile = None                    # computed in _computeZipFile
        self.directory = None                  # Computed in __extractZipFile
        self.entries = []                      # Computed in __extractZipFile
        self.filesByExtension = {}             # Computed in __extractZipFile
        self._computeZipFile()
        self.__extractZipFile()
        self._checkZipTestSuite()
        TestSuite.__init__(
            self,
            useFile = self._computeUseFile(),
            stateFiles = self._computeStateFiles(),
            testId = self._computeTestId(testId))

    def free(self, targetDirectoryToBeRemoved=None):
        """
        Free temporary resources if any.
        If a targetDirectory is specified as a parameter, check if this was
        the same directory given when the ZipTestSuite was created and if
        this is so, remove this whole directory.
        """
        if self.isZipRemote:
            log.info('Removing temporary local zip file: %s', self.zipFile)
            os.remove(self.zipFile)
        if self.targetDirectory is None:
            log.info(
                'Removing temporary directory %s (used to extract zip file)'
                % self.directory)
            shutil.rmtree(self.directory)
        else:
            if targetDirectoryToBeRemoved == self.targetDirectory:
                log.info('Removing target directory as requested: %s'
                         % targetDirectoryToBeRemoved)
                shutil.rmtree(targetDirectoryToBeRemoved)
            else:
                raise Exception(
                    'ERROR: trying to free %s while %s was created. No removal'
                    % (targetDirectoryToBeRemoved, self.targetDirectory))


    def _computeZipFile(self):
        """
        Compute self.zipFile from zipFileId
        :param zipFileId: a path to a local zip file or url to remote zipfile
        :type zipFileId: str
        """
        protocols = ['http', 'https', 'ftp', 'ftps']
        self.isZipRemote = any(
            self.zipFileId.startswith(p + '://') for p in protocols)
        if self.isZipRemote:
            (_, file) = tempfile.mkstemp(suffix='.zip')
            self.zipFile = file
            log.info('Downloading zip file from %s into %s'
                % (self.zipFileId, self.zipFile))
            urllib.urlretrieve(self.zipFileId, self.zipFile)
        else:
            self.zipFile = self.zipFileId


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
        print '----', self.filesByExtension
        use_files = self.filesByExtension['.use']
        if len(use_files) == 1:
            return use_files[0]
        else:
            raise Exception('More than one .use file: %s'  % use_files )


    def _computeStateFiles(self):
        """
        Select the state files form all the soil files in the archives.
        This function could be overriden.
        :return: a list of soil file that will serve as the state files
        :rtype: [str]
        """
        return self.filesByExtension['.soil']

    def _computeSelectEntry(self, file):
        """
        Indicate if the zip entry
        :param file: the name of the zip entryu
        :type file: str
        :return: return True if the entry must be selected
        :rtype: book
        """
        extension = os.path.splitext(file)[1]
        return (
            self.extractOnly is None
            or (self.extractOnly is not None
                and extension in self.extractOnly))

    def _checkZipTestSuite(self):
        pass


    def __extractZipFile(self):
        # compute target_directory
        if self.targetDirectory is None:
            self.directory = tempfile.mkdtemp(prefix='zipTestSuite_')
        else:
            if os.path.isdir(self.targetDirectory):
                raise IOError('ERROR: %s is not a directory'
                              % self.targetDirectory)
            self.directory = self.targetDirectory
        if not zipfile.is_zipfile(self.zipFile):
            raise IOError('ERROR: %s is not a zip file' % self.zipFile)

        log.info('Extracting files from %s' % self.zipFile)

        with zipfile.ZipFile(self.zipFile, 'r') as z:
            if z.testzip() != None:
                raise IOError('ERROR: %s contains bad files' % self.zipFile)
            for entry in z.namelist():
                if os.path.isabs(entry):
                    raise IOError(
                        'ERROR: %s contains absolute files' % self.zipFile)
                log.info('Extracting files from %s' % self.zipFile)
                if self._computeSelectEntry(entry):
                    log.info('  Extracting entry %s' % entry)
                    self.__extractZipEntry(z,entry)
                else:
                    log.info('  Skipping file %s' % entry)

    def __extractZipEntry(self, zipHandle, entry):
        zipHandle.extract(entry, self.directory)
        expected = os.path.normpath(os.path.join(self.directory, entry))
        if not os.path.exists(expected):
            raise IOError(
                'Cannot extract %s from %s keeping this name'
                % (entry, self.zipFileId))
        self.entries.append(expected)
        extension = os.path.splitext(entry)[1]
        if os.path.isfile(expected):
            if extension not in self.filesByExtension:
                self.filesByExtension[extension] = []
            self.filesByExtension[extension].append(expected)
        return expected

class CrossTestSuite(object):
    __test__ = False  # To avoid being taken as a test by nose
    pass














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
        # (empty and erroneous files skipped)
        if self.isCorrect:
            for state_file in self.stateFiles:
                self.__evaluateAssertionsFromState(state_file)

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
        Evaluatin the assertions contained in the given state file.
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

import zipfile
import os.path
import tempfile
import urllib
import shutil




class ZipTestSuite(TestSuite):
    """
    Test suite represented as a local or remote zip file
    The _compute methods can be overriden if needed to change the behavior
    of this class.
    """
    __test__ = False  # To avoid being taken as a test by nose

    def __init__(self, zipFileId, testId=None,
                 targetDirectory = None, extractOnly=('.soil', '.use'),
                 useFileShortName = None):
        """
        Build a USE OCL test suite by extracting the .use file and .soil
        file from an archive.
        :param zipFileId: A URL to a zip file (in this case it will be
        downloaded) or a path to a local zip file.
        :type zipFileId: str
        :param testId:
        :type testId:
        :param targetDirectory: The directory where to extract the zip file.
        :type targetDirectory: str
        :param extractOnly: A list of extensions with (e.g. ".soil"). Only
            files with these extensions will be extracted. If none, all files
            will be extracted.
        :type extractOnly: [str]
        :param useFileShortName:
        :type useFileShortName:
        :return:
        :rtype:
        """
        self.zipFileId = zipFileId
        self.targetDirectory = targetDirectory
        self.extractOnly = extractOnly
        self.isZipRemote = None                 # computed in _computeZipFile
        self.zipFile = None                     # computed in _computeZipFile
        self.directory = None                   # Computed in __extractZipFile
        self.useFileShortName = useFileShortName
        self.entries = []                       # Computed in __extractZipFile
        self.filesByExtension = {}              # Computed in __extractZipFile
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
        Try to Free temporary resources if any.
        If a targetDirectory is specified as a parameter, check if this was
        the same directory given when the ZipTestSuite was created and if
        this is so, remove this whole directory.
        If a file or directory cannot be removed just add a warning in the
        log. This may be because another process is using the file.
        """
        if self.isZipRemote:
            log.info('Removing temporary local zip file: %s', self.zipFile)
            try:
                os.remove(self.zipFile)
            except:
                log.warning('Cannot remove %s' % self.zipFile)

        if self.targetDirectory is None:
            log.info(
                'Removing temporary directory %s (used to extract zip file)'
                % self.directory)
            try:
                shutil.rmtree(self.directory)
            except:
                log.warning('Cannot remove directory %s' % self.directory)
        else:
            if targetDirectoryToBeRemoved == self.targetDirectory:
                log.info('Removing target directory as requested: %s'
                         % targetDirectoryToBeRemoved)
                try:
                    shutil.rmtree(targetDirectoryToBeRemoved)
                except:
                    log.warning('Cannot remove directory %s'
                                % targetDirectoryToBeRemoved)
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
        """
        Return the name of the file corresponding "the" .use file.
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





class CrossZipTestSuite(object):
    __test__ = False  # To avoid being taken as a test by nose
    def __init__(self, idsAndZips,
                 targetDirectory=None, extractOnly=('.soil', '.use')):
        for (id,zip) in idsAndZips:
            pass


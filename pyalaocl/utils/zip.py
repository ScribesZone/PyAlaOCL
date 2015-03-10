# coding=utf-8


import zipfile
import os.path
import tempfile
import urllib
import shutil

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

class ZipArtefact(object):
    """
    Extraction of a zip, either local or remote.
    The _compute methods can be overriden if needed to change the behavior
    of this class.
    """

    def __init__(self, zipFileId,
                 targetDirectory=None, filter=None, ignoreMacOsDirectory=True):
        """
        Extract a file structure from a zip, either local or remote zip.
        :param zipFileId: A URL to a zip file (in this case it will be
        downloaded) or a path to a local zip file.
        :type zipFileId: str
        :param targetDirectory: The directory where to extract the zip file.
            If none a directory will be created in a temporary place.
        :type targetDirectory: str
        :param filter: This value is interpreted by the _doFilter method.
            This method can be overridden and this parameter is interpreted
            accordingly. In the default implementation the filter is a
            list of extensions with (e.g. ".java"). Only files with these
            extensions will be extracted. If None, is given all files
            will be extracted.
        :type filter: any
        """
        self.zipFileId = zipFileId
        """ URL or filename of the zip file"""

        self.targetDirectory = targetDirectory
        """ Directory where to extract the zip. This will be in a temporary
        place if no targetDirectory is given as a parameter. """

        self.filter = filter
        """ Filter interpreted by the function _ """

        self.isZipRemote = None  # computed in _computeZipFile
        """ Indicate if the original zip was remote or not """

        self.zipFile = None  # computed in _computeZipFile
        """ Path to the local or downloaded zipfile """

        self.directory = None  # Computed in __extractZipFile
        """ The directory where the zip is extracted.
            Same value as targetDirectory unless this parameter
            is not defined. In this case this will be a directory
            in a temporary place.
        """

        self.ignoreMacOsDirectory = ignoreMacOsDirectory

        self.entries = []  # Computed in __extractZipFile
        self.filesByExtension = {}  # Computed in __extractZipFile
        self._getZipFile()
        self.__extractZipFile()
        self._checkZipContent()


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


    def _getZipFile(self):
        """
        Compute self.zipFile from zipFileId. This implementation download
        the zip file from the URL if zipFileId is an URL. Otherwise it assume
        that this is a local file. Set self.zipFile based on self.zipFileId.
        If the zip file is downloaded, it is downloaded in a temporary place.
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


    def _doFilter(self, file):
        """
        Indicate if the zip entry should be selected or not according to
        the filter given. This implementation assume that the filter is
        a list of extensions (e.g. .java). Only file with these extensions
        are retained.
        :param file: the name of the zip entryu
        :type file: str
        :return: return True if the entry must be selected
        :rtype: bool
        """
        extension = os.path.splitext(file)[1]
        return (
            self.filter is None
            or (self.filter is not None
                and extension in self.filter))


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
                if (not self._doFilter(entry)):
                    log.info('  Skipping entry (due to filter) %s ',entry)
                elif (entry.startswith('__MACOSX/')
                      and self.ignoreMacOsDirectory):
                    log.info('  Skipping MacOsX entry %s ',entry)
                else:
                    self.__extractZipEntry(z, entry)


    def __extractZipEntry(self, zipHandle, entry):
        extension = os.path.splitext(entry)[1]
        log.info('  Extracting %s entry %s ', extension, entry)
        zipHandle.extract(entry, self.directory)
        expected = os.path.normpath(os.path.join(self.directory, entry))
        if not os.path.exists(expected):
            raise IOError(
                'Cannot extract %s from %s keeping this name'
                % (entry, self.zipFileId))
        self.entries.append(expected)
        # log.debug('Entry %s, Extension: %s, Expected: %s',
        #         entry, extension, expected)
        if os.path.isfile(expected):
            if extension not in self.filesByExtension:
                self.filesByExtension[extension] = []
            self.filesByExtension[extension].append(expected)
        return expected


    def _checkZipContent(self):
        pass

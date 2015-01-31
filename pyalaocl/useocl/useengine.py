# coding=utf-8

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

import os
import tempfile
import operator
import re

_RES_DIRECTORY = os.path.join(os.path.abspath(
    os.path.dirname(__file__)),'res')
_USE_DIRECTORY = os.path.join(_RES_DIRECTORY,'use-3.0.6')

class USEEngine(object):

    USE_OCL_COMMAND = os.path.join(_USE_DIRECTORY,'bin','use')

    """
    Name of the use command.
    If the default value ('use') does not work, for instance if
    the use binary is not in the system path, you can change this
    value either in the source, or programmatically using
    USEEngine.USE_OCL_COMMAND = r'c:\Path\To\UseCommand\bin\use'
    """

    command = None
    """ Last command executed by the engine"""

    commandExitCode = None
    """ Exit code of last execution"""

    out = None
    """ output of last execution (in case of separated out/err)"""

    err = None
    """ errors of last execution (in case of separated out/err)"""

    outAndErr = None
    """ output/errors of last execution if merged out/err """


    @classmethod
    def __soilHelper(cls, name):
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'res', name)


    @classmethod
    def __execute(cls, useFile, soilFile, errWithOut=False):
        """ Execute use command with the given model and given soil file.
        The soil file must terminate by a 'quit' statement so that the process
        finish.
        """
        def readAndRemove(filename):
            with open(filename, 'r') as f:
                _ = f.read()
            os.remove(filename)
            return _

        if errWithOut:
            #-- one unique output file for output and errors
            (f, output_filename) = tempfile.mkstemp(suffix='.txt', text=True)
            os.close(f)
            errors_filename = None
            redirection = '>%s 2>&1' % output_filename
            cls.out = None
            cls.err = None
        else:
            # -- two temporary files for output and errors
            (f, output_filename) = tempfile.mkstemp(suffix='.use', text=True)
            os.close(f)
            # prepare temporary file for errors
            (f, errors_filename) = tempfile.mkstemp(suffix='.err', text=True)
            os.close(f)
            redirection = '>%s 2>%s' % (output_filename, errors_filename)
            cls.outAndErr = None


        commandPattern = '%s -nogui %s %s '+ redirection
        cls.command = (commandPattern
                           % (cls.USE_OCL_COMMAND, useFile, soilFile))

        # Execute the command
        log.info('Execute USE OCL: %s', cls.command)
        cls.commandExitCode = os.system(cls.command)
        log.info('Execute USE OCL returned %s exit code', cls.commandExitCode)

        if errWithOut:
             if cls.commandExitCode != 0:
                 cls.outAndErr = None
             else:
                 cls.outAndErr = readAndRemove(output_filename)
        else:
            cls.out = readAndRemove(output_filename)
            cls.err = readAndRemove(errors_filename)

        return cls.commandExitCode


    @classmethod
    def useVersion(cls):
        cls.__execute(
            cls.__soilHelper('empty.use'),
            cls.__soilHelper('quit.soil'))
        first_line = cls.out.split('\n')[0]
        m = re.match( r'use version (?P<version>[0-9\.]+),', first_line)
        if m:
            return m.group('version')
        else:
            raise EnvironmentError('Cannot execute USE OCL or get its version. Is this program installed?')



    @classmethod
    def analyzeUSEModel(cls, useFileName):
        cls.__execute(
            useFileName,
            cls.__soilHelper('infoModelAndQuit.soil'))
        return cls.commandExitCode



    @classmethod
    def evaluateSoilFilesWithUSEModel(cls, modelFile, stateFiles):

        def __generateSoilValidationDriver(stateFilePaths):
            """
            Create a soil sequence with the necessary statements to drive the
            sequence of state validation. That is, it loads and checks each
            state one after each other.

            The soil driver sequence generated looks like:
                    reset
                    open file1.soil
                    check
                    reset
                    open file2.soil
                    check
                    ...
                    quit

            The output with error messages can be found after the execution
            in the variable outAndErr.
            :param stateFilePaths: A list of .soil files corresponding
            to states.
            :type stateFilePaths: [str]
            :return: The soil text
            :rtype: str
            """
            lines = reduce(operator.add,
                           map(
                               lambda file: ['reset', 'open ' + file,
                                             'check -d'],
                               stateFilePaths))
            lines.append('quit')
            return '\n'.join(lines)

        #-- generate soil driver
        driver_sequence = __generateSoilValidationDriver(stateFiles)
        (f, driver_filename) = tempfile.mkstemp(suffix='.soil', text=True)
        os.close(f)
        with open(driver_filename, 'w') as f:
            f.write(driver_sequence)

        cls.__execute(
            modelFile,
            driver_filename)

        return cls.outAndErr

# coding=utf-8


# FIXME
USE_OCL_COMMAND = 'use'


import os
import tempfile
import operator


class USEEngine(object):

    _soilHelperDirectory = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', '..', 'res')

    commandExitCode = None
    command = None
    out = None
    err = None
    outAndErr = None


    @classmethod
    def analyzeUSEModel(cls, useFileName):
        soil_file = os.path.join(
            cls._soilHelperDirectory, 'infoModelAndQuit.soil')

        # prepare temporary file for output
        (f, output_filename) = tempfile.mkstemp(suffix='.use', text=True)
        os.close(f)

        # prepare temporary file for errors
        (f, errors_filename) = tempfile.mkstemp(suffix='.err', text=True)
        os.close(f)

        cls.outAndErr = None
        cls.command = '%s -nogui %s %s >%s 2>%s' \
              % (USE_OCL_COMMAND, useFileName, soil_file,
                 output_filename, errors_filename)

        # Execute the command
        cls.commandExitCode = os.system(cls.command)

        # Read errors
        with open(errors_filename, 'r') as f:
            cls.err = f.read()
        os.remove(errors_filename)

        # Read output
        with open(output_filename, 'r') as f:
            cls.out = f.read()
        os.remove(output_filename)

        return cls.commandExitCode



    @classmethod
    def evaluateSoilFilesWithUSEModel(cls, modelFile, stateFiles):

        def __generateSoilValidationDriver(stateFilePaths):
            """
            Create a soil sequence with the necessary statements to drive the
            sequence of state validation. That is, it loads and checks each
            state one after each other.

            The soil driver sequence generated look like:
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

        #-- prepare output file
        (f, output_filename) = tempfile.mkstemp(suffix='.txt', text=True)
        os.close(f)

        cls.out = None
        cls.err = None
        #-- execute the command
        cls.command = '%s -nogui %s %s >%s 2>&1' \
                        % (
            USE_OCL_COMMAND, modelFile, driver_filename, output_filename)
        cls.commandExitCode = os.system(cls.command)

        #-- process the result
        if cls.commandExitCode != 0:
            cls.outAndErr = None
        else:
            with open(output_filename, 'r') as f:
                cls.outAndErr = f.read()

        #-- cleaning
        os.remove(output_filename)
        os.remove(driver_filename)
        return cls.outAndErr

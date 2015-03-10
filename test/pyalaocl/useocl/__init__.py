# coding=utf-8
import os
import glob

TEST_CASES_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'testcases')

# TEST_SOIL_DIRECTORY = os.path.join(TEST_CASES_DIRECTORY, 'soil')

def getFile(name, prefixes):
    if os.path.isabs(name):
        return name
    else:
        return os.path.join(*[TEST_CASES_DIRECTORY] + prefixes + [name])

def getUseFile(name):
    return getFile(name,[])

def getSoilFile(name):
    return getFile(name, ['soil'])

def getSoilFileList(nameOrList):
    if isinstance(nameOrList, basestring):
        # add the prefix if necessary
        with_prefix = getFile(nameOrList, ['soil'])
        return glob.glob(with_prefix)
    else:
        return map(getSoilFile, nameOrList)

def getZipFile(name):
    for prefix in ['http:','https:','ftp:','ftps:']:
        if name.startswith(prefix):

            return name
    return getFile(name, ['zip'])

def setup():
    pass

def teardown():
    pass

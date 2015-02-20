# coding=utf-8
import os

TEST_CASES_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'testcases')

TEST_SOIL_DIRECTORY = os.path.join(TEST_CASES_DIRECTORY, 'soil')

def getUseFile(name):
    return os.path.join(TEST_CASES_DIRECTORY, name)

def getSoilFile(name):
    return os.path.join(TEST_SOIL_DIRECTORY, name)

def setup():
    pass


def teardown():
    pass

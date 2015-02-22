# coding=utf-8

from test.pyalaocl.useocl import getUseFile
import pyalaocl.useocl.printer
import pyalaocl.useocl.analyzer

def testGenerator_UseOCLPrinter():
    test_cases = [
        {'use': 'Demo.use'},
        {'use': 'AssociationClass.use'},
        {'use': 'CarRental.use'},
        {'use': 'Sudoku.use'},
    ]
    for test_case in test_cases:
        test_name = test_case['use']
        check_UseOCLPrinter.description = test_name
        yield check_UseOCLPrinter, test_case


def check_UseOCLPrinter(case):
    useFile = getUseFile(case['use'])
    model = pyalaocl.useocl.analyzer.UseOCLModel(useFile).model
    printer = pyalaocl.useocl.printer.UseOCLPrinter(model)
    print printer.do()

# coding=utf-8
# coding=utf-8

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

# test_cases_dir = pyalaocl.test.useocl.
#
# os.path.join(
#     os.path.dirname(os.path.abspath(__file__)),
#     '..', 'test', 'testcases', 'soil')
# test_files = [f
#               for f in os.listdir(test_cases_dir) if f.endswith('.soil')]
#
# for test_file in test_files:
#     print '-' * 10 + ' Parsing %s\n\n' % test_file
#     use = pyalaocl.useocl.analyzer.UseOCLModel(
#         test_cases_dir + os.sep + test_file)
#     if use.isValid:
#         print use.model
#     else:
#         print >> sys.stderr, 'Failed to create canonical form'
#         for error in use.errors:
#             print >> sys.stderr, error
#             # UseOCLConverter.convertCanOCLInvariants(use.canonicalLines)

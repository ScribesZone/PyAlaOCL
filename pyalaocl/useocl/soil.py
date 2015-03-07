# coding=utf-8

"""
Interpreter of soil specifications. Not fully implemented.
"""

import os
import re
from collections import OrderedDict

import pyalaocl.useocl.analyzer as analyser

import pyalaocl.useocl.state
from pyalaocl.useocl.state import State, Object, Link, LinkObject



def isEmptySoilFile(file):
    with open(file) as f:
        content = f.read()
    match = re.search(r'(^ *!)|(^ *open)', content, re.MULTILINE)
    return match is None


class UseSoilSpecification(object):
    def __init__(self, useSoilFile):
        if not os.path.isfile(useSoilFile):
            raise Exception('File "%s" not found' % useSoilFile)
        self.fileName = useSoilFile
        self.sourceLines = tuple(
            open(useSoilFile, 'r').read().splitlines())
        self.directory = os.path.dirname(useSoilFile)
        self.isValid = None
        self.errors = []
        self.lines = None
        self.ignoredLines = []

        self.state = State()

# SOIL Syntax
# http://useocl.sourceforge.net/wiki/index.php/SOIL
# s ::=                                     (statement)
#    v := new c [(nameExpr)] |              (object creation)
#    v := new c [(nameExpr)] between (participant1,participant2,...) |
#                                           (link object creation)
#    destroy e  |                           (object destruction)
#    insert (e1; ... ; en) into a j |       (link insertion)
#    delete (e1; ... ; en) from a j |       (link deletion)
#    e1.a := e2 |                           (attribute assignment)
#    v := e |                               (variable assignment)
#    e1.op(e2; ... ; en) |                  (operation call)
#    v := e1.op(e2; ... ; en) |             (operation call with result)
#    [begin] s1; ... ; sn [end] [declare v1 : t1; ... ; vn : tn] |
#                                           (block of statements)
#    if e then s1 [else s2] end |           (conditional execution)
#    for v in e do s end                    (iteration)

    def execute(self, prefix=r'^'):
        begin = prefix + r' *! *'
        end = ' *$'
        for line in self.sourceLines:

            #--- object creation ----------------------------------------------
            r = begin+r'create +(?P<name>\w+) *: *(?P<className>\w+)'+end
            m = re.match(r, line)
            if m:
                # print 'object %s : %s' % (m.group('name'),m.group('className'))
                Object(self.state, m.group('className'),m.group('name'))
                continue

            #--- attribute assignement ----------------------------------------
            r = (begin
                    + r'(set)? +(?P<name>\w+) *'
                    + r'\. *(?P<attribute>\w+) *'
                    + r':= *(?P<value>.*)'
                    + end )
            m = re.match(r, line)
            if m:
                # print 'attribute %s.%s = %s' % (
                #    m.group('name'), m.group('attribute'), m.group('value'))
                object = self.state.objects[m.group('name')]
                object.set(m.group('attribute'),m.group('value'))
                continue

            #--- link creation-------------------------------------------------
            r = (begin
                 + r'insert *\((?P<objectList>[\w, ]+)\) *'
                 + r'into +'
                 + r'(?P<associationName>\w+)'
                 + end )
            m = re.match(r, line)
            if m:
                #print 'link %s(%s)' % (
                #    m.group('associationName'), m.group('objectList'))
                object_names = m.group('objectList').replace(' ','').split(',')
                objects = [ self.state.objects[object_name]
                            for object_name in object_names ]
                Link(self.state, m.group('associationName'), objects)
                continue

            #--- link object creation -----------------------------------------
            r = (begin
                 + r'create +(?P<name>\w+) *: *(?P<className>\w+) +'
                 + r'between +\((?P<objectList>[\w, ]+)\) *'
                 + end )
            m = re.match(r, line)
            if m:
                class_name = m.group('className')
                name = m.group('name')
                object_names = m.group('objectList').replace(' ','').split(',')
                objects = [self.state.objects[object_name]
                           for object_name in object_names]
                LinkObject(self.state, class_name, name, objects)
                continue

            #--- object (or link object) destruction --------------------------
            r = (begin+ r'destroy +(?P<name>\w+)'+ end )
            m = re.match(r, line)
            if m:
                name = m.group('name')
                # check if this is an regular object or a link object
                if name in self.state.objects:
                    del self.state.objects[name]
                else:
                    del self.state.linkObject[name]
                continue

            #--- link destruction ---------------------------------------------
            r = (begin
                 + r'delete *\((?P<objectList>[\w, ]+)\)'
                 + r' +from +(?P<associationName>\w+)'
                 + end )
            m = re.match(r, line)
            if m:
                object_names = \
                    m.group('objectList').replace(' ', '').split(',')
                link_name = '_'.join(object_names)
                del self.state.links[link_name]


            #---- blank lines -------------------------------------------------
            r = r'^ *$'
            m = re.match(r, line)
            if m:
                continue

            #---- unknown or unimplemented commands ---------------------------
            raise NotImplementedError(line)

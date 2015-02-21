# coding=utf-8

"""
Simple metamodel for object states. Contains definitions for:

- State,
- Object,
- Link,
- LinkObject.
"""

from collections import OrderedDict

class State(object):
    def __init__(self):
        self.objects = OrderedDict()
        self.links = OrderedDict()
        self.linkObject = OrderedDict()



class StateElement(object):
    def __init__(self, state):
        self.state = state


class Object(StateElement):
    def __init__(self, state, className, name):
        super(Object,self).__init__(state)
        state.objects[name] = self
        self.name = name
        self.className = className
        self.attributes = OrderedDict()

    def set(self, name, value):
        self.attributes[name] = value



class Link(StateElement):
    def __init__(self, state, associationName, objects):
        super(Link, self).__init__(state)
        link_name = '_'.join(map(lambda o: o.name, objects))
        state.links[link_name] = self
        self.associationName = associationName
        self.roles = objects



class LinkObject(StateElement):
    def __init__(self, state, associationClassName, name, objects) :
        super(LinkObject, self).__init__(state)
        state.linkObject[name] = self
        self.name = name
        self.className = associationClassName
        self.attributes = OrderedDict()
        self.roles = objects

    def set(self, name, value):
        self.attributes[name] = value


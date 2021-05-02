#!/bin/env python3

import yaml
import types


"""
A very simplified C++ metamodel for documentation purpose only.
"""

class CppElement(yaml.YAMLObject):
    """
    A C++ metamodel element
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'

def documented_trait(defined=None, name=None):
    """
    A documented element
    """
    if defined is None:
        defined = CppElement()
    defined.briefdescription = None
    defined.detaileddescription = None
    defined.name = name
    defined.location = None
    return defined

def macro_trait(defined=None):
    """
    A macro found in the C++ include files
    """
    defined = documented_trait(defined)
    defined.location = None
    return defined

def variable_trait(defined=None):
    """
    A variable, constant, constexpr, etc...
    """
    if defined is None:
        defined = CppElement()
    self.type = None
    self.initializer = None
    return defined

def variable_trait(defined=None):
    """
    A function
    """
    if defined is None:
        defined = CppElement()
    defined.type = None
    defined.initializer = None
    return defined

def function_trait(defined=None):
    """
    A function
    """
    if defined is None:
        defined = CppElement()
    defined.parameters = {}
    defined.result = result_trait()
    return defined

def parameter_trait(defined=None):
    """
    A function parameter
    """
    defined = documented_trait(defined)
    defined.type = None
    defined.default_value = None
    return defined
    
def result_trait(defined=None):
    """
    A function result
    """
    if defined is None:
        defined = CppElement()
    defined.briefdescription = None
    defined.detaileddescription = None
    defined.type = None
    return defined

def enum_value_trait(name=None, defined=None):
    """
    An enum value
    """
    defined = documented_trait(defined, name)
    defined.initializer = None
    return defined

def enum_trait(defined=None):
    """
    A C++ enum
    """
    if defined is None:
        defined = CppElement()
    defined.kind = 'enum'
    defined.type = None
    defined.values = []
    defined.strongly_typed = False
    return defined

def typeref_trait(defined=None, type=None):
    """
    An element of C++ that references a type
    """
    if defined is None:
        defined = CppElement()
    defined.kind = 'typedef'
    defined.type = type
    return defined

def member_function_trait(defined=None):
    """
    a member function is similar to a free or static function but it has an
    additional implicit "this" parameter.
    """
    function_trait(defined)
    defined.mutable = True
    defined.virtual = 'no'
    return defined
    
def class_definition_trait(defined=None,name=None):
    """
    A definition in a class, with a visibility attribute
    """
    defined = documented_trait(defined, name)
    setattr(type(defined), '__getattr__', defined_reflect_get)
    setattr(type(defined), '__setattr__', defined_reflect_set)
    defined.visibility = 'public'
    return defined

def class_def_trait(defined=None,name=None):
    """
    A definition in a class, with a visibility attribute
    """
    defined = documented_trait(defined, name)
    setattr(type(defined), '__getattr__', defined_reflect_get)
    setattr(type(defined), '__setattr__', defined_reflect_set)
    defined.visibility = 'public'
    return defined

def class_trait(defined=None):
    """
    A class or struct
    """
    if defined is None:
        defined = CppElement()
    defined.kind = 'class'
    defined.types = {}
    defined.functions = {}
    defined.variables = {}
    defined.member_functions = {}
    defined.member_variables = {}
    return defined

def defined_reflect_set(self, name, value):
    if name == "defined":
        self.__dict__ |= value.__dict__
    else:
        self.__dict__[name] = value

def defined_reflect_get(self, name):
    if name == "defined":
        return self
    else:
        raise AttributeError("'CppElement' object has no attribute '{}'".format(name))

def ns_def_trait(defined=None, name=None):
    """
    A named (namespaced) definition of a C++ element that can be referenced.
    """
    return documented_trait(defined, name)

def namespace_trait(defined=None):
    """
    A C++ namespace
    """
    if defined is None:
        defined = CppElement()
    defined.namespaces = {}
    defined.types = {}
    defined.functions = {}
    defined.variables = {}
    return defined

#!/bin/env python3

from collections import defaultdict

"""
A simplified C++ metamodel for documentation purpose only.

We do not take into account the distinction between declaration and definition
here.
"""

class Macro:
    """
    A macro found in the C++ include files
    """
    
    def __init__(self):
        self.briefdescription = None
        self.detaileddescription = None
        self.name = None
        self.location = None

def Template(Templated):
    class TemplatedTemplate(Templated):
        """
        A C++ template
        """
        
        class Parameter:
            """
            A type parameter as used in template 
            """
            
            def __init__(self):
                self.default = None
        
        def __init__(self):
            Templated.__init__(self)
            self.parameters = []
            self.templated = None

class Variable:
    """
    A variable, constant, constexpr, etc...
    """
    
    def __init__(self):
        self.type = None
        self.initializer = None

class Function:
    """
    A function
    """
    
    class Parameter:
        def __init__(self):
            self.briefdescription = None
            self.detaileddescription = None
            self.name = None
            self.location = None
            self.type = None
            self.default_value = None
    
    class Result:
        def __init__(self):
            self.briefdescription = None
            self.detaileddescription = None
            self.type = None
    
    def __init__(self):
        self.parameters = {}
        self.result = Function.Result()

class Enum_:
    """
    A C++ enum
    """
    
    class Value:
        """
        An enum value
        """
        
        def __init__(self, name=None):
            self.briefdescription = None
            self.detaileddescription = None
            self.name = name
            self.location = None
            self.initializer = None

    def __init__(self):
        self.type = None
        self.values = []
        self.strongly_typed = False

class TypeRef:
    """
    An element of C++ that references a type
    """
    
    def __init__(self):
        self.type = None

class ReferenceTypeRef(TypeRef):
    """
    A way to type something by referencing an existing type and adding it the 
    C++ reference modifier (&)
    """
    
    def __init__(self):
        TypeRef.__init__(self)

class ConstTypeRef(TypeRef):
    """
    A way to type something by referencing an existing type and adding it the 
    const modifier
    """
    def __init__(self):
        TypeRef.__init__(self)

class PointerTypeRef(TypeRef):
    """
    A way to type something by referencing an existing type and adding it the 
    pointer modifier (*)
    """
    def __init__(self):
        TypeRef.__init__(self)

class RvalueReferenceTypeRef(TypeRef):
    """
    A way to type something by referencing an existing type and adding it the 
    C++ rvalue-reference modifier (&&)
    """
    def __init__(self):
        TypeRef.__init__(self)

class TemplateRef:
    """
    A way to type something by referencing a type template and associating
    arguments to the template parameters, i.e. a template instanciation.
    """
    
    class Argument:
        """
        A type argument as used is in template instanciations
        """
        def __init__(self):
            self.parameter
            self.value
    
    def __init__(self):
        self.template = None
        self.arguments = []

class Class_:
    """
    A class or struct
    """

    class Function(Function):
        """
        a Class_.Function is similar to a free or static function but it has an
        additional implicit "this" parameter.
        """
        
        def __init__(self):
            Function.__init__(self)
            self.mutable = True
            self.virtual = 'no'
    
    class Variable(Variable):
        """
        a Class_.Variable is similar to a free or static variable but it depends
        on a class instance.
        """
        
        def __init__(self):
            Variable.__init__(self)
    
    class Definition:
        """
        A definition in a class, with a visibility attribute
        """
        
        def __init__(self, name=None, defined=None):
            self.briefdescription = None
            self.detaileddescription = None
            self.name = name
            self.location = None
            self.visibility = 'public'
            self.defined = defined

    def __init__(self):
        self.kind = 'class'
        self.classes = {}
        self.typedefs = {}
        self.enums = {}
        self.functions = {}
        self.variables = {}
        self.member_functions = {}
        self.member_variables = {}

class Namespace:
    """
    A C++ namespace
    """

    class Definition:
        """
        A named (namespaced) definition of a C++ element that can be referenced.
        """
        
        def __init__(self, name=None, defined=None):
            self.briefdescription = None
            self.detaileddescription = None
            self.name = name
            self.location = None
            self.defined = defined

    def __init__(self):
        self.namespaces = {}
        self.classes = {}
        self.typedefs = {}
        self.enums = {}
        self.functions = {}
        self.variables = {}

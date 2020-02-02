#!/bin/env python3

import yaml

"""
A simplified C++ metamodel for documentation purpose only.

We do not take into account the distinction between declaration and definition
here.
"""

class Macro(yaml.YAMLObject):
    """
    A macro found in the C++ include files
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    def __init__(self):
        self.briefdescription = None
        self.detaileddescription = None
        self.name = None
        self.location = None

def Template(Templated):
    class TemplatedTemplate(yaml.YAMLObject, Templated):
        """
        A C++ template
        """
        
        yaml_tag = 'tag:yaml.org,2002:map'
        
        class Parameter(yaml.YAMLObject):
            """
            A type parameter as used in template 
            """
            
            yaml_tag = 'tag:yaml.org,2002:map'
            
            def __init__(self):
                self.default = None
        
        def __init__(self):
            Templated.__init__(self)
            self.parameters = []
            self.templated = None

class Variable(yaml.YAMLObject):
    """
    A variable, constant, constexpr, etc...
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    def __init__(self):
        self.type = None
        self.initializer = None

class Function(yaml.YAMLObject):
    """
    A function
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    class Parameter(yaml.YAMLObject):
        
        yaml_tag = 'tag:yaml.org,2002:map'
        
        def __init__(self):
            self.briefdescription = None
            self.detaileddescription = None
            self.name = None
            self.location = None
            self.type = None
            self.default_value = None
    
    class Result(yaml.YAMLObject):
        
        yaml_tag = 'tag:yaml.org,2002:map'
        
        def __init__(self):
            self.briefdescription = None
            self.detaileddescription = None
            self.type = None
    
    def __init__(self):
        self.parameters = {}
        self.result = Function.Result()

class Enum_(yaml.YAMLObject):
    """
    A C++ enum
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    class Value(yaml.YAMLObject):
        """
        An enum value
        """
        
        yaml_tag = 'tag:yaml.org,2002:map'
        
        def __init__(self, name=None):
            self.briefdescription = None
            self.detaileddescription = None
            self.name = name
            self.location = None
            self.initializer = None

    def __init__(self):
        self.kind = 'enum'
        self.type = None
        self.values = []
        self.strongly_typed = False

class TypeRef(yaml.YAMLObject):
    """
    An element of C++ that references a type
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    def __init__(self, type=None):
        self.kind = 'typedef'
        self.type = type

class ReferenceTypeRef(TypeRef):
    """
    A way to type something by referencing an existing type and adding it the 
    C++ reference modifier (&)
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    def __init__(self):
        TypeRef.__init__(self)

class ConstTypeRef(TypeRef):
    """
    A way to type something by referencing an existing type and adding it the 
    const modifier
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    def __init__(self):
        TypeRef.__init__(self)

class PointerTypeRef(TypeRef):
    """
    A way to type something by referencing an existing type and adding it the 
    pointer modifier (*)
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    def __init__(self):
        TypeRef.__init__(self)

class RvalueReferenceTypeRef(TypeRef):
    """
    A way to type something by referencing an existing type and adding it the 
    C++ rvalue-reference modifier (&&)
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
    def __init__(self):
        TypeRef.__init__(self)

class TemplateRef:
    """
    A way to type something by referencing a type template and associating
    arguments to the template parameters, i.e. a template instanciation.
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'
    
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

class Class_(yaml.YAMLObject):
    """
    A class or struct
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'

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
        
        yaml_tag = 'tag:yaml.org,2002:map'
        
        def __init__(self):
            Variable.__init__(self)
    
    class Definition(yaml.YAMLObject):
        """
        A definition in a class, with a visibility attribute
        """
    
        yaml_tag = 'tag:yaml.org,2002:map'
        
        def __init__(self, name=None, defined=None):
            self.briefdescription = None
            self.detaileddescription = None
            self.name = name
            self.location = None
            self.visibility = 'public'
            self.defined = defined

    def __init__(self):
        self.kind = 'class'
        self.types = {}
        self.functions = {}
        self.variables = {}
        self.member_functions = {}
        self.member_variables = {}

class Namespace(yaml.YAMLObject):
    """
    A C++ namespace
    """
    
    yaml_tag = 'tag:yaml.org,2002:map'

    class Definition(yaml.YAMLObject):
        """
        A named (namespaced) definition of a C++ element that can be referenced.
        """
    
        yaml_tag = 'tag:yaml.org,2002:map'
        
        def __init__(self, name=None, defined=None):
            self.briefdescription = None
            self.detaileddescription = None
            self.name = name
            self.location = None
            self.defined = defined

    def __init__(self):
        self.namespaces = {}
        self.types = {}
        self.functions = {}
        self.variables = {}

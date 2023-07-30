# CythonPEG

Description of Cython syntax in pyparsings PEG syntax.  
Allows for the auto generation of cython->python STUB files.  

There are a few assumptions that need to be made when converting from cython to python.  
-How to handle the types that don't exist in python?  
&emsp;-types are currently pulled verbatim, even if they dont exist in python (pylance handles bad typing pretty well)  
-How to handle syntax that does not exist in python?  
&emsp;-structs are translated to classes (maybe will change to dataclass in the future)

90% of cython files and desired capability from a stub file are present.  
-function and method function name completion   
-doc string stransfer (only tribble quote supported)  

I have tested against my own cython files.  It works to an acceptable level.  
Imports, and other small type changes can be modified manually. 

# Example Usage
input pyx
```
from cython_peg import cython2stub

cython_file = \
"""

def python_function1(a : Dict[Dict[int, int], int], b = {1: [1, 2, 3]}) -> int:
    """complex type return and assignment parsing"""
    return 1

cdef int function2(int a, int b):
    """cdef returns and typing"""
    return 1

cpdef float function3(int a, List[int] = [1, 2, 3, 4]):
    """cpdef return, typing, and assignment """
    return 1.0

cdef struct Struct2D:
    """simple struct with cython types"""
    float64** data
    size_t[2] shape

cdef class OuterClass(object):
    """documentation of outer class"""
    cdef class InnerClass(object):
        """document of inner class"""
        cdef int method1(int a, int b):
            """inner method"""
            return 1
    cdef int method2(float a, float b):
        """outer method"""
        return 1

cdef float[:, :] memmoryviewfunction(float[:, :]):
    return None
"""

print(cython_string_2_stub(cython_file))
```
output pyi
```
def python_function1(a: Dict[Dict[int, int], int], b={1 : [1, 2, 3]}) -> int:
    """complex type return and assignment parsing"""
    ...

def function2(a: int, b: int) -> int:
    """cdef returns and typing"""
    ...

class Struct2D:
    """simple struct with cython types"""
    float64** data
    size_t[2] shape

class OuterClass:
    """documentation of outer class"""

    class InnerClass:
        """document of inner class"""

        def method1(a: int, b: int) -> int:
            """inner method"""
            ...

    def method2(a: float, b: float) -> int:
        """outer method"""
        ...

```

# maintenance and updates

There is a single python file that contains all the cython (pyx) definitions for parsing and reconstruction into python stub files.  
This is not a module.  You are intended to modify the parsing definitions for your desired stub (pyi) output.

The entirety of the cython syntax is probably not captured in the parsing definitions.  
Additionally, how certain cython syntax is translated will probably need customization for each project. The pyparsing definitions allow for easy customization. https://pyparsing-docs.readthedocs.io/en/latest/index.html

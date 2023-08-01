def python_function1(a : Dict[Dict[int, int], int], b = {1: [1, 2, 3]}) -> int:
    """complex type return and assignment parsing"""
    return 1


undefined parsing data
Parsing does not know how to parse this

cdef float64 function2(int a, int b):
    """cdef returns and typing"""
    return

cpdef double function3(int a, List[int] b = [1, 2, 3, 4]):
    """cpdef return, typing, and assignment """
    return

cdef struct Struct2D:
    """simple struct with cython types"""
    float64** data
    size_t[2] shape

# bad syntax parser will not parse
cdef struct int Struct5D:
    size_t a
    float32* data

@dataclass
class DataStructure:
    """simple datastruct docs"""
    a: int
    b: int
    c: str

cdef class OuterClass(object):
    """documentation of outer class"""

    cdef class InnerClass(object):
        """document of inner class"""

        cdef List method1(int a, int b):
            """inner method"""
            return [1, 2, 3, 4, 5]

    cdef List method2(float a, float b):
        """outer method"""
        return [1, 2, 3, 4, 5]

cdef float[:, :] memmoryviewfunction(float[:, :] input_view):
    """simple doc"""
    return input_view

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
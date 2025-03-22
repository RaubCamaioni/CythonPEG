from typing import List

cdef class OuterClass(object):
    """documentation of outer class"""

    cdef List method2(self, float a, float b):
        """outer method"""
        return [1, 2, 3, 4, 5]

cdef class InnerClass(object):
    """document of inner class"""

    cdef List method1(self, int a, int b):
        """inner method"""
        return [1, 2, 3, 4, 5]
from typing import List

# Defining a public function with Cython type annotations
cdef double add_and_multiply(double x, double y):
    # Variables and constants
    cdef double result
    cdef int i
    cdef double pi = 3.14159

    # Basic arithmetic operations
    result = x + y
    result *= pi

    return result

cpdef double function3(str a, List[int] b = [1, 2, 3, 4]):
    """cpdef return, typing, and assignment """
    return 10


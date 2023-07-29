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

# Defining a public function with C data types
cdef int fibonacci(int n):
    """some sort of algorithm?"""
    # Using conditionals and loops
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        cdef int a = 0
        cdef int b = 1
        cdef int i
        for i in range(2, n+1):
            a, b = b, a + b

        return b

# Defining a public function with memoryviews
cpdef int sum_array(int[:] arr):
    # Using memoryviews and array operations
    cdef int total = 0
    for i in range(arr.shape[0]):
        total += arr[i]

    return total

# Defining a public class with methods
cdef class Point:
    # Class attributes
    cdef double x
    cdef double y

    # Class methods with typed arguments and return values
    cdef double distance_to_origin(self):
        """calculate some distance stuff"""
        return (self.x**2 + self.y**2)**0.5

    cdef double distance_to_point(self, double x2, double y2):
        return ((self.x - x2)**2 + (self.y - y2)**2)**0.5

# Using external C libraries
cdef extern from "math.h":
    double sin(double)

# Defining a public function that uses an external C function
cpdef double compute_sin(double angle):
    return sin(angle)
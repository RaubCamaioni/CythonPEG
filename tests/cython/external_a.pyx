# Using external C libraries
cdef extern from "math.h":
    double sin(double)

# Defining a public function that uses an external C function
cpdef double compute_sin(double angle):
    return sin(angle)

# Defining a public function that uses an external C function
cpdef double compute_sin(double angle):
    return sin(angle)
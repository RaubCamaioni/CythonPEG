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
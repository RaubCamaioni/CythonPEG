ctypedef double float64

cdef struct Struct2D:
    float64** data
    size_t[2] shape
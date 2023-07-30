

cdef class MyClass(object):

    test:str
    cdef int test_def(self, int num):
        return num * num

    cpdef float test_cdef(self, long num):
        return num * num

    def float test_cpdef(self, long num):
        return num * num

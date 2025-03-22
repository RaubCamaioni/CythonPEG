# Defining a public function with C data types
cdef int fibonacci(int n):
    """some sort of algorithm?"""
    cdef int a = 0
    cdef int b = 1
    cdef int i

    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a = 0
        b = 1
        for i in range(2, n+1):
            a, b = b, a + b
        return b
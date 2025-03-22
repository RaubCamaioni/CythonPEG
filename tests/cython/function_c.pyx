# Defining a public function with memoryviews
cpdef int sum_array(int[:] arr):
    # Using memoryviews and array operations
    cdef int total = 0
    for i in range(arr.shape[0]):
        total += arr[i]

    return total
from enum import Enum

ctypedef double float64

def python_function1(a: Dict[Dict[int, int], int], b = {1: [1, 2, 3]}) -> int:
    """complex type return and assignment parsing"""
    return 1

cdef float64 function2(int a, int b):
    """cdef returns and typing"""
    return a + b

class MyEnum(Enum):
    A = 0
    B = 0

def test2(interp_flag: MyEnum = MyEnum.A):
    return

def test3(self, **_kwargs: dict):
    return
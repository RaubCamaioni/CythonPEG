# additional static imports
import numpy as np
float64 = float32 = double = long = longlong = float
uint64 = uint32 = uint16 = uint8 = short = int

from enum import Enum

float64 = double

def python_function1(a: Dict[Dict[int, int], int], b={1 : [1, 2, 3]}) -> int:
    """complex type return and assignment parsing"""
    ...

def function2(a: int, b: int) -> float64:
    """cdef returns and typing"""
    ...

class MyEnum(Enum):
    A = 0
    B = 0

def test2(interp_flag: MyEnum=MyEnum.A):
    ...

# additional static imports
import numpy as np
float64 = float32 = double = long = longlong = float
uint64 = uint32 = uint16 = uint8 = short = int

from enum import Enum

class SimpleClass:
    """simple docs"""

    class SimpleInnerClass(Enum):
        """inner enum for organizing"""
        a: int
        b: int

    def __init__(self, a):
        ...

    def simple_method(self, a: int) -> int:
        """simple method docs"""
        ...

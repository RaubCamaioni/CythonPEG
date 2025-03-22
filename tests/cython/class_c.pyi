# additional static imports
import numpy as np
float64 = float32 = double = long = longlong = float
uint64 = uint32 = uint16 = uint8 = short = int

from typing import List

class OuterClass(object):
    """documentation of outer class"""

    def method2(self, a: float, b: float) -> List:
        """outer method"""
        ...

class InnerClass(object):
    """document of inner class"""

    def method1(self, a: int, b: int) -> List:
        """inner method"""
        ...

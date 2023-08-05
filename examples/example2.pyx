import moduleA
import moduleB, moduleC
from moudleA import (
    moduleD, 
    moduleE, 
    moduleF
)
from moduleA import functionA, funtion2
from moduleA.moduleB import methodA

def python_function1(a: Dict[Dict[int, int], int], b = {1: [1, 2, 3]}) -> int:
    """complex type return and assignment parsing"""
    return 1

cdef float64 function2(int a, int b):
    """cdef returns and typing"""
    return

def test2(interp_flag: int = myenum.SIMPLE_ENUM):
    return

cpdef double function3(str a = cv2.METHOD, List[int] b = [1, 2, 3, 4]):
    """cpdef return, typing, and assignment """
    return

cdef struct Struct2D:
    """simple struct with cython types"""
    float64** data
    size_t[2] shape

@dataclass
class DataStructure:
    """simple datastruct docs"""
    a: int
    b: int
    c: str

class SimpleClass:
    """simple docs"""

    class SimpleInnerClass(Enum):
        """inner enum for organizing"""
        a: int
        b: int

    def __init__(self, a):
        pass

    def simple_method(self, a: int) -> int:
        """simple method docs"""
        return 1

cdef class OuterClass(object):
    """documentation of outer class"""

    cdef class InnerClass(object):
        """document of inner class"""

        cdef List method1(int a, int b):
            """inner method"""
            return [1, 2, 3, 4, 5]

    cdef List method2(float a, float b):
        """outer method"""
        return [1, 2, 3, 4, 5]

cdef float[:, :] memmoryviewfunction(float[:, :] input_view):
    """simple doc"""
    return input_view

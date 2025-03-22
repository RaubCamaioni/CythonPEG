# additional static imports
import numpy as np
float64 = float32 = double = long = longlong = float
uint64 = uint32 = uint16 = uint8 = short = int

class Point:

    def distance_to_origin(self) -> double:
        """calculate some distance stuff"""
        ...

    def distance_to_point(self, x2: double, y2: double) -> double:
        ...

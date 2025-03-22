__version__ = "0.1.0"

from cythonpeg.utilities import set_type_converter_partial, set_type_converter_complete
from cythonpeg.tree2string import set_indent, cython_string_2_stub
import logging

logging.basicConfig(level=logging.INFO)

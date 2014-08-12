""" Functionality for composing shaders from multiple GLSL code snippets.
"""

from .program import ModularProgram  # noqa
from .function import (Function, MainFunction, Variable, Varying,  # noqa
                       FunctionChain)  # noqa
from .compiler import Compiler  # noqa

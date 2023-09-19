from uplc.ast import Program as UPLCProgram

from .optimize.patterns import PatternReplacer
from .pluthon_ast import Program, AST
from .util import NoOp


def compile(x: Program, optimize_patterns=True) -> UPLCProgram:
    """
    Returns compiles Pluto code in UPLC
    :param x: the program to compile
    :param optimize_patterns: whether to optimize patterns i.e. write them out and reuse by calling. This decreases the size of the compiled program but increases the execution time.
    """
    for step in [PatternReplacer() if optimize_patterns else NoOp()]:
        x = step.visit(x)
    x = x.compile()
    return x


def dumps(u: AST):
    return u.dumps()

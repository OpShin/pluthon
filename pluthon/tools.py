from uplc.ast import Program as UPLCProgram

from .optimize.patterns import OncePatternReplacer
from .optimize.constant_index_access_list import ConstantIndexAccessOptimizer
from .optimize.fast_index_access_list import FastIndexAccessOptimizer
from .pluthon_ast import Program, AST
from .util import NoOp


def compile(
    x: Program, optimize_patterns=True, unsafe_index_access=False
) -> UPLCProgram:
    """
    Returns compiles Pluto code in UPLC
    :param x: the program to compile
    :param optimize_patterns: whether to optimize patterns i.e. write them out and reuse by calling. This decreases the size of the compiled program but increases the execution time.
    """
    x_old_dumps = None
    x_new_dumps = x.dumps()
    # need to iterate so that pattern optimizations can be applied to patterns that are part of other patterns
    # we stop when a fixpoint is reached
    while x_new_dumps != x_old_dumps:
        x_old_dumps = x_new_dumps
        for step in [
            ConstantIndexAccessOptimizer(),
            FastIndexAccessOptimizer() if unsafe_index_access else NoOp(),
            OncePatternReplacer() if optimize_patterns else NoOp(),
        ]:
            x = step.visit(x)
        x_new_dumps = x.dumps()
    x = x.compile()
    return x


def dumps(u: AST):
    return u.dumps()

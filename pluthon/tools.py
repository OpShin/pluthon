from uplc.ast import Program as UPLCProgram

from .compiler_config import DEFAULT_CONFIG
from .optimize.constant_index_access_list import IndexAccessOptimizer
from .optimize.patterns import OncePatternReplacer, AllPatternReplacer
from .pluthon_ast import Program, AST
from .util import NoOp


def compile(
    x: Program,
    config=DEFAULT_CONFIG,
) -> UPLCProgram:
    """
    Returns compiled Pluto code in UPLC
    :param x: the program to compile
    """
    x_old_dumps = None
    x_new_dumps = x.dumps()
    # need to iterate so that pattern optimizations can be applied to patterns that are part of other patterns
    # we stop when a fixpoint is reached
    while x_new_dumps != x_old_dumps:
        x_old_dumps = x_new_dumps
        for step in [
            IndexAccessOptimizer() if config.constant_index_access_list else NoOp(),
            (
                (
                    OncePatternReplacer()
                    if config.iterative_unfold_patterns
                    else AllPatternReplacer()
                )
                if config.compress_patterns
                else NoOp()
            ),
        ]:
            x = step.visit(x)
        x_new_dumps = x.dumps()
    x = x.compile()
    return x


def dumps(u: AST):
    return u.dumps()

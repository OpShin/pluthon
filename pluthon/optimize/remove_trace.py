from pluthon.pluthon_ast import Apply, BuiltIn, Force
from pluthon.util import NodeTransformer
from uplc import ast as uplc_ast


class RemoveTrace(NodeTransformer):
    """
    Replaces Trace with just the argument
    """

    def visit_Apply(self, node: Apply):
        if (
            isinstance(node.f, Force)
            and isinstance(node.f.x, BuiltIn)
            and node.f.x.builtin == uplc_ast.BuiltInFun.Trace
        ):
            return node.xs[1]
        return self.generic_visit(node)

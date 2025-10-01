from pluthon.pluthon_ast import Apply, BuiltIn, Force, Text
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
            # only remove traces that trace a constant string
            # otherwise there might be side effects we are removing
            and isinstance(node.xs[0], Text)
        ):
            return node.xs[1]
        return self.generic_visit(node)

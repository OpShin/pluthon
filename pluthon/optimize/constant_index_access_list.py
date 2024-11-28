from pluthon.pluthon_ast import Integer
from pluthon.pluthon_sugar import (
    IndexAccessList,
    ConstantIndexAccessList,
    NthField,
    ConstantNthField,
    IndexAccessListFast,
    ConstantIndexAccessListFast,
)
from pluthon.util import NodeTransformer


class IndexAccessOptimizer(NodeTransformer):
    """
    Replaces IndexAccesses to constants with ConstantIndexAccesses
    """

    def visit_IndexAccessList(self, node: IndexAccessList):
        if isinstance(node.i, Integer):
            return ConstantIndexAccessList(node.l, node.i.x)
        return node

    def visit_NthField(self, node: NthField):
        if isinstance(node.n, Integer):
            return ConstantNthField(node.d, node.n.x)
        return node

    def visit_IndexAccessListFast(self, node: IndexAccessListFast):
        if isinstance(node.i, Integer):
            return ConstantIndexAccessListFast(node.l, node.i.x)
        return node

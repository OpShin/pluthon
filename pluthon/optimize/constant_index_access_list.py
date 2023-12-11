from pluthon import IndexAccessList, Integer, ConstantIndexAccessList
from pluthon.util import NodeTransformer


class IndexAccessOptimizer(NodeTransformer):
    """
    Replaces IndexAccesses to constants with ConstantIndexAccesses
    """

    def visit_IndexAccessList(self, node: IndexAccessList):
        if isinstance(node.i, Integer):
            return ConstantIndexAccessList(node.l, node.i.x)
        return node

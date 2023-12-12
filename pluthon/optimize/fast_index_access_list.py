from pluthon import (
    IndexAccessList,
    Integer,
    ConstantIndexAccessList,
    UnsafeConstantIndexAccessList,
    UnsafeIndexAccessList,
)
from pluthon.util import NodeTransformer


class FastIndexAccessOptimizer(NodeTransformer):
    """
    Replaces IndexAccesses to constants with ConstantIndexAccesses
    """

    def visit_IndexAccessList(self, node: IndexAccessList):
        return UnsafeIndexAccessList(node.l, node.i)

    def visit_ConstantIndexAccessList(self, node: ConstantIndexAccessList):
        return UnsafeConstantIndexAccessList(node.l, node.i)

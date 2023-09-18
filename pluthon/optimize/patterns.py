import dataclasses
from typing import Type

from .. import PVar, PLambda, PLet
from ..pluthon_ast import Pattern, Program, Apply
from ..util import NodeTransformer, NodeVisitor, iter_fields


class PatternCollector(NodeVisitor):
    def __init__(self):
        self.pattern_classes = set()

    def visit(self, node):
        """Visit a node."""
        while isinstance(node, Pattern):
            # Patterns are special
            self.pattern_classes.add(type(node))
            node = node.compose()
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)


def make_abstract_function(pattern_class: Type[Pattern]):
    fields = dataclasses.fields(pattern_class)
    return PLambda(
        [f.name for f in fields],
        pattern_class(*[PVar(f.name) for f in fields]).compose(),
    )


def make_abstract_function_name(pattern_class: Type[Pattern]):
    return f"p_{pattern_class.__name__}"


class PatternReplacer(NodeTransformer):
    def visit(self, node):
        """Visit a node."""
        if isinstance(node, Pattern):
            # Patterns are special
            pattern_var = PVar(make_abstract_function_name(type(node)))
            node = Apply(
                pattern_var,
                *(field for _, field in iter_fields(node)),
            )
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_Program(self, node: Program):
        pattern_collector = PatternCollector()
        pattern_collector.visit(node)
        pattern_classes = pattern_collector.pattern_classes
        # TODO should we not somehow figure out interdependencies here
        term = PLet(
            [
                (
                    make_abstract_function_name(pattern_class),
                    self.visit(make_abstract_function(pattern_class)),
                )
                for pattern_class in pattern_classes
            ],
            self.visit(node.prog),
        )
        return Program(
            version=node.version,
            prog=term,
        )

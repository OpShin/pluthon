import dataclasses
from typing import Type

from .. import PVar, PLambda, PLet
from ..pluthon_ast import Pattern, Program, Apply
from ..util import NodeTransformer, NodeVisitor, iter_fields


class PatternCollector(NodeVisitor):
    def __init__(self):
        self.pattern_classes = set()
        self.pattern_classes_in_dep_order = list()

    def visit(self, node):
        """Visit a node."""
        added_patterns = []
        while isinstance(node, Pattern):
            # Patterns are special
            # we collect them here and later add them in reverse order
            # after subpatterns are added recursively
            # this ensures that the outermost pattern is added last
            node_type = type(node)
            if node_type not in self.pattern_classes:
                added_patterns.append(node_type)
            self.pattern_classes.add(node_type)
            node = node.compose()
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        res = visitor(node)
        self.pattern_classes_in_dep_order.extend(reversed(added_patterns))
        return res


def make_abstract_function(pattern_class: Type[Pattern]):
    fields = dataclasses.fields(pattern_class)
    if fields:
        return PLambda(
            [f.name for f in fields],
            pattern_class(*[PVar(f.name) for f in fields]).compose(),
        )
    else:
        return pattern_class().compose()


def make_abstract_function_name(pattern_class: Type[Pattern]):
    return f"p_{pattern_class.__name__}"


class PatternReplacer(NodeTransformer):
    def visit(self, node):
        """Visit a node."""
        if isinstance(node, Pattern):
            # Patterns are special
            pattern_var = PVar(make_abstract_function_name(type(node)))
            fields = list(iter_fields(node))
            if fields:
                node = Apply(
                    pattern_var,
                    *(field for _, field in iter_fields(node)),
                )
            else:
                node = pattern_var
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_Program(self, node: Program):
        pattern_collector = PatternCollector()
        pattern_collector.visit(node)
        pattern_classes = pattern_collector.pattern_classes_in_dep_order
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

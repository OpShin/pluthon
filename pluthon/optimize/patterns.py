import dataclasses
from collections import defaultdict
from typing import Type
from graphlib import TopologicalSorter

from .. import PVar, PLambda, PLet
from ..pluthon_ast import Pattern, Program, Apply
from ..util import NodeTransformer, NodeVisitor, iter_fields


class PatternCollector(NodeVisitor):
    def __init__(self):
        self.patterns = set()

    def visit(self, node):
        """Visit a node."""
        if isinstance(node, Pattern):
            # Patterns are special
            # we collect them here and later add them in reverse order
            # after subpatterns are added recursively
            # this ensures that the outermost pattern is added last
            node_type = type(node)
            self.patterns.add(node_type)
            res = self.visit(node.compose())
        else:
            method = "visit_" + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            res = visitor(node)
        return res


class PatternDepBuilder(NodeVisitor):
    def __init__(self):
        self.pattern_deps = defaultdict(set)

    def patterns_in_dep_order(self):
        ts = TopologicalSorter(self.pattern_deps)
        return ts.static_order()

    def visit(self, node):
        """Visit a node."""
        if isinstance(node, Pattern):
            # Patterns are special
            # we collect them here and later add them in reverse order
            # after subpatterns are added recursively
            # this ensures that the outermost pattern is added last
            node_type = type(node)
            # compose but without actual variables to avoid collecting patterns that are passed into the pattern
            subpattern_collector = PatternCollector()
            subpattern_collector.visit(make_abstract_function(node_type))
            subpatterns = subpattern_collector.patterns
            self.pattern_deps[node_type].update(subpatterns)
            res = self.visit(node.compose())
        else:
            method = "visit_" + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            res = visitor(node)
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
        pattern_collector = PatternDepBuilder()
        pattern_collector.visit(node)
        pattern_classes = pattern_collector.patterns_in_dep_order()
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

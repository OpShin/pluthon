import dataclasses
import uuid
from collections import defaultdict
from copy import deepcopy
from functools import lru_cache
from typing import Type
from graphlib import TopologicalSorter
from ordered_set import OrderedSet

from .. import PVar, PLambda, PLet, Ite
from ..pluthon_ast import Pattern, Program, Apply, Force, Delay, Var, Lambda
from ..util import NodeTransformer, NodeVisitor, iter_fields


class EvaluatedVariableCollector(NodeVisitor):
    def __init__(self):
        self.evaluated_variables = OrderedSet()

    def visit_Var(self, node: Var):
        self.evaluated_variables.add(node.name)


class ConditionallyEvaluatedVariableCollector(NodeVisitor):
    def __init__(self):
        self.conditionally_evaluated_variables = OrderedSet()

    def visit_Ite(self, node: Ite):
        then_branch_evaluated_variables_collector = EvaluatedVariableCollector()
        then_branch_evaluated_variables_collector.visit(node.t)
        self.conditionally_evaluated_variables.update(
            then_branch_evaluated_variables_collector.evaluated_variables
        )
        else_branch_evaluated_variables_collector = EvaluatedVariableCollector()
        else_branch_evaluated_variables_collector.visit(node.e)
        self.conditionally_evaluated_variables.update(
            else_branch_evaluated_variables_collector.evaluated_variables
        )

    def visit_Delay(self, node: Delay):
        evaluated_variables_collector = EvaluatedVariableCollector()
        evaluated_variables_collector.visit(node.x)
        self.conditionally_evaluated_variables.update(
            evaluated_variables_collector.evaluated_variables
        )

    def visit_Lambda(self, node: Lambda):
        evaluated_variables_collector = EvaluatedVariableCollector()
        evaluated_variables_collector.visit(node.term)
        self.conditionally_evaluated_variables.update(
            evaluated_variables_collector.evaluated_variables
        )


@lru_cache()
def conditionally_evaluated_params(pattern_class: Type[Pattern]):
    """
    taint analysis to figure out if parameters to a pattern are involved conditionally -> if so, we need to wrap them in a delay
    """
    # we generate unique identifiers for all parameters of the pattern
    # to detect which of them are used conditionally
    fields = dataclasses.fields(pattern_class)
    uuid_map = {f.name: PVar(f"{f.name}_{uuid.uuid4().hex}").name for f in fields}
    if fields:
        term = pattern_class(*[Var(uuid_map[f.name]) for f in fields]).compose()
    else:
        term = pattern_class().compose()
    conditionally_evaluated_variables_collector = (
        ConditionallyEvaluatedVariableCollector()
    )
    conditionally_evaluated_variables_collector.visit(term)
    return {
        f.name
        for f in fields
        if uuid_map[f.name]
        in conditionally_evaluated_variables_collector.conditionally_evaluated_variables
    }


class PatternCollector(NodeVisitor):
    def __init__(self):
        self.patterns = dict()

    def visit(self, node):
        """Visit a node."""
        if isinstance(node, Pattern):
            # Patterns are special
            # we collect them here and later add them in reverse order
            # after subpatterns are added recursively
            # this ensures that the outermost pattern is added last
            node_type = type(node)
            self.patterns[node_type] = None
            res = self.visit(node.compose())
        else:
            method = "visit_" + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            res = visitor(node)
        return res


class PatternDepBuilder(NodeVisitor):
    def __init__(self):
        self.pattern_deps = dict()
        self.pattern_occurrences = defaultdict(int)

    def patterns_in_dep_order(self):
        """
        Returns the patterns in dependency order, i.e. the ones that are used in other patterns are defined first
        """
        ts = TopologicalSorter(self.pattern_deps)
        return ts.static_order()

    def visit(self, node):
        """Visit a node."""
        if isinstance(node, Pattern):
            # Patterns are special
            node_type = type(node)
            self.pattern_occurrences[node_type] += 1
            # compose but without actual variables to avoid collecting patterns that are passed into the pattern
            subpattern_collector = PatternCollector()
            subpattern_collector.visit(make_abstract_function(node_type))
            subpatterns = subpattern_collector.patterns
            self.pattern_deps.setdefault(node_type, OrderedSet()).update(subpatterns)
            res = self.visit(node.compose())
        else:
            method = "visit_" + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            res = visitor(node)
        return res


@lru_cache()
def make_abstract_function(pattern_class: Type[Pattern]):
    fields = dataclasses.fields(pattern_class)
    cep = conditionally_evaluated_params(pattern_class)
    if fields:
        return PLambda(
            [f.name for f in fields],
            pattern_class(
                *[
                    Force(PVar(f.name)) if f.name in cep else PVar(f.name)
                    for f in fields
                ]
            ).compose(),
        )
    else:
        return pattern_class().compose()


def make_abstract_function_name(pattern_class: Type[Pattern]):
    return f"p_{pattern_class.__name__}"


class OncePatternReplacer(NodeTransformer):
    """
    Replaces the innermost pattern in terms of dependencies, i.e. the one that has to be defined
    last in topological order
    """

    unfold_pattern_class = None

    def visit(self, node):
        """Visit a node."""
        if self.unfold_pattern_class is not None and isinstance(
            node, self.unfold_pattern_class
        ):
            # Patterns are special
            if self.unfold_pattern_occurrences > 1:
                pattern_var = PVar(make_abstract_function_name(type(node)))
                fields = list(iter_fields(node))
                cep = conditionally_evaluated_params(type(node))
                if fields:
                    node = Apply(
                        pattern_var,
                        *(
                            Delay(field) if name in cep else field
                            for name, field in iter_fields(node)
                        ),
                    )
                else:
                    node = pattern_var
            else:
                node = node.compose()
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_Program(self, node: Program):
        pattern_collector = PatternDepBuilder()
        pattern_collector.visit(node)
        pattern_classes = list(pattern_collector.patterns_in_dep_order())
        if pattern_classes:
            self.unfold_pattern_class = pattern_classes[-1]
            self.unfold_pattern_occurrences = pattern_collector.pattern_occurrences[
                self.unfold_pattern_class
            ]
            if self.unfold_pattern_occurrences > 1:
                # if the pattern occurs more than once, we need to define it as a function
                # otherwise we can just inline it
                term = PLet(
                    [
                        (
                            make_abstract_function_name(self.unfold_pattern_class),
                            self.visit(
                                deepcopy(
                                    make_abstract_function(self.unfold_pattern_class)
                                )
                            ),
                        ),
                    ],
                    self.visit(node.prog),
                )
            else:
                term = self.visit(node.prog)
        else:
            term = self.visit(node.prog)
        self.unfold_pattern_class = None
        return Program(
            version=node.version,
            prog=term,
        )


class AllPatternReplacer(NodeTransformer):
    def visit(self, node):
        """Visit a node."""
        if isinstance(node, Pattern):
            # Patterns are special
            pattern_var = PVar(make_abstract_function_name(type(node)))
            fields = list(iter_fields(node))
            cep = conditionally_evaluated_params(type(node))
            if fields:
                node = Apply(
                    pattern_var,
                    *(
                        Delay(field) if name in cep else field
                        for name, field in iter_fields(node)
                    ),
                )
            else:
                node = pattern_var
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_Program(self, node: Program):
        pattern_collector = PatternDepBuilder()
        pattern_collector.visit(node)
        pattern_classes = list(pattern_collector.patterns_in_dep_order())
        if pattern_classes:
            term = PLet(
                [
                    (
                        make_abstract_function_name(pattern_class),
                        self.visit(deepcopy(make_abstract_function(pattern_class))),
                    )
                    for pattern_class in pattern_classes
                ],
                self.visit(node.prog),
            )
        else:
            term = node.prog
        return Program(
            version=node.version,
            prog=term,
        )

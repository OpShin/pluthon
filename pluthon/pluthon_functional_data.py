from .pluthon_ast import (
    ByteString,
    Integer,
    Bool,
    AST,
    Apply,
    Delay,
    Ite,
    Unit,
    Force,
    Pattern,
)
from .pluthon_sugar import (
    EqualsByteString,
    EqualsInteger,
    EqualsBool,
    PVar,
    PLambda,
    TraceError,
)
from dataclasses import field, dataclass
import typing

"""
Functional Data Structures that can store anything (as opposed to PlutusData derivatives)

Built on wrapped lambda terms
"""


def identity(x):
    return x


_BUILTIN_TYPE_MAP = {
    bytes: (ByteString, identity),
    str: (ByteString, lambda x: x.encode()),
    int: (Integer, identity),
    bool: (Bool, identity),
}

_EQUALS_MAP = {
    ByteString: EqualsByteString,
    Integer: EqualsInteger,
    Bool: EqualsBool,
}


def FunctionalMapExtend(
    old_statemonad: "FunctionalMap",
    names: typing.List[typing.Any],
    values: typing.List[AST],
) -> "FunctionalMap":
    additional_compares = Apply(
        old_statemonad,
        PVar("x"),
        PVar("def"),
    )
    for name, value in zip(names, values):
        keytype, transform = _BUILTIN_TYPE_MAP[type(name)]
        additional_compares = Ite(
            _EQUALS_MAP[keytype](PVar("x"), keytype(transform(name))),
            Delay(value),
            additional_compares,
        )
    return PLambda(
        ["x", "def"],
        additional_compares,
    )


class FunctionalMap(AST):
    # low level maps that only support equal type keys
    # but can store anything
    def __new__(
        cls, kv: typing.Optional[typing.Dict[typing.Any, AST]] = None
    ) -> "FunctionalMap":
        res = PLambda(["x", "def"], PVar("def"))
        if kv is not None:
            res = FunctionalMapExtend(res, kv.keys(), kv.values())
        return res


@dataclass
class FunctionalMapAccess(Pattern):
    m: AST
    k: AST
    default: AST = field(default_factory=lambda: TraceError("KeyError"))

    def compose(self):
        return Force(Apply(self.m, self.k, Delay(self.default)))


TOPRIMITIVEVALUE = b"0"


class WrappedValue(AST):
    def __new__(cls, uplc_obj: AST, attributes: FunctionalMap):
        updated_map = FunctionalMapExtend(attributes, [TOPRIMITIVEVALUE], [uplc_obj])
        return updated_map


def from_primitive(p: AST, attributes: AST):
    return WrappedValue(p, attributes)


def to_primitive(wv: WrappedValue):
    return Apply(wv, TOPRIMITIVEVALUE, Unit())


class FunctionalTuple(AST):
    def __new__(cls, *vs: AST) -> "FunctionalTuple":
        # idea: just construct a nested if/else comparison
        if not vs:
            return Unit()
        param_name = "__f__"
        return PLambda([param_name], Apply(PVar(param_name), *map(Delay, vs)))


class FunctionalTupleAccess(AST):
    def __new__(cls, tuple: AST, index: int, size: int):
        if size == 0:
            raise ValueError("Can not access elements of an empty tuple")
        return Apply(
            tuple, PLambda([f"v{i}" for i in range(size)], Force(PVar(f"v{index}")))
        )

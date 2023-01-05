from .pluthon_sugar import *
import typing

"""
Functional Data Structures that can store anything (as opposed to PlutusData derivatives)

Built on wrapped lambda terms
"""

_BUILTIN_TYPE_MAP = {
    bytes: (ByteString, id),
    str: (ByteString, lambda x: x.encode()),
    int: (Integer, id),
    bool: (Bool, id),
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
        Var("x"),
        Var("def"),
    )
    for name, value in zip(names, values):
        keytype, transform = _BUILTIN_TYPE_MAP[type(name)]
        additional_compares = Ite(
            _EQUALS_MAP[keytype](Var("x"), keytype(transform(name))),
            value,
            additional_compares,
        )
    return Lambda(
        ["x", "def"],
        additional_compares,
    )


class FunctionalMap(AST):
    # low level maps that only support equal type keys
    # but can store anything
    def __new__(
        cls, kv: typing.Optional[typing.Dict[typing.Any, AST]] = None
    ) -> "FunctionalMap":
        res = Lambda(["x", "def"], Var("def"))
        if kv is not None:
            res = FunctionalMapExtend(res, kv.keys(), kv.values())
        return res


def FunctionalMapAccess(m: AST, k: AST, default=Trace(Text("KeyError"), Error())):
    return Apply(m, k, default)


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
        param = Var("__f__")
        return Lambda([param.name], Apply(param, vs))


class FunctionalTupleAccess(AST):
    def __new__(cls, tuple: AST, index: int, size: int):
        return Apply(Lambda([f"v{i}" for i in range(size)], Var(f"v{index}")), tuple)

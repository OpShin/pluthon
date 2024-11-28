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
    Lambda,
    Var,
    Let,
    Text,
    BuiltIn,
    Error,
)
from uplc import ast as uplc_ast
import typing
from dataclasses import field, dataclass

########## Pluto Abstractions that simplify handling complex structures ####################


def name_scheme_compatible_varname(x: str):
    return f"0{x}_"


def PVar(x: str):
    """
    A simple wrapper around Var to ensure adherence to the naming scheme
    :param x: name of the variable
    :return: variable for use with pluthon, adhering to the naming scheme
    """
    return Var(name_scheme_compatible_varname(x))


def PLambda(vars: typing.List[str], term: AST):
    """
    A simple wrapper around Lambda to ensure adherence to the naming scheme
    """
    return Lambda(list(map(name_scheme_compatible_varname, vars)), term)


def PLet(bindings: typing.List[typing.Tuple[str, AST]], term: AST):
    """
    A simple wrapper around Let to ensure adherence to the naming scheme
    """
    return Let([(name_scheme_compatible_varname(x), y) for x, y in bindings], term)


@dataclass
class RecFun(Pattern):
    x: AST

    def compose(self):
        return PLet(
            [("g", self.x)],
            Apply(PVar("g"), PVar("g")),
        )


@dataclass
class Not(Pattern):
    x: AST

    def compose(self):
        return IfThenElse(self.x, Bool(False), Bool(True))


@dataclass
class Iff(Pattern):
    x: AST
    y: AST

    def compose(self):
        return PLet([("y", self.y)], Ite(self.x, PVar("y"), Not(PVar("y"))))


@dataclass
class And(Pattern):
    x: AST
    y: AST

    def compose(self):
        return Ite(self.x, self.y, Bool(False))


@dataclass
class Or(Pattern):
    x: AST
    y: AST

    def compose(self):
        return Ite(self.x, Bool(True), self.y)


@dataclass
class Xor(Pattern):
    x: AST
    y: AST

    def compose(self):
        return PLet([("y", self.y)], Ite(self.x, Not(PVar("y")), PVar("y")))


@dataclass
class Implies(Pattern):
    x: AST
    y: AST

    def compose(self):
        return Ite(self.x, self.y, Bool(True))


def wrap_builtin_binop(b: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST):
        return Apply(BuiltIn(b), x, y)

    return wrapped


def wrap_builtin_binop_force(b: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST):
        return Apply(Force(BuiltIn(b)), x, y)

    return wrapped


def wrap_builtin_binop_force_force(b: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST):
        return Apply(Force(Force(BuiltIn(b))), x, y)

    return wrapped


def wrap_builtin_ternop(t: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST, z: AST):
        return Apply(BuiltIn(t), x, y, z)

    return wrapped


def wrap_builtin_ternop_force(t: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST, z: AST):
        return Apply(Force(BuiltIn(t)), x, y, z)

    return wrapped


def wrap_builtin_ternop_force_force(t: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST, z: AST):
        return Apply(Force(Force(BuiltIn(t))), x, y, z)

    return wrapped


def wrap_builtin_unop(u: uplc_ast.BuiltInFun):
    def wrapped(x: AST):
        return Apply(BuiltIn(u), x)

    return wrapped


def wrap_builtin_unop_force(u: uplc_ast.BuiltInFun):
    def wrapped(x: AST):
        return Apply(Force(BuiltIn(u)), x)

    return wrapped


def wrap_builtin_unop_force_force(u: uplc_ast.BuiltInFun):
    def wrapped(x: AST):
        return Apply(Force(Force(BuiltIn(u))), x)

    return wrapped


def wrap_builtin_hexop_force(u: uplc_ast.BuiltInFun):
    def wrapped(d: AST, v: AST, w: AST, x: AST, y: AST, z: AST):
        return Apply(Force(BuiltIn(u)), d, v, w, x, y, z)

    return wrapped


AddInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.AddInteger)
SubtractInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.SubtractInteger)
MultiplyInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.MultiplyInteger)
DivideInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.DivideInteger)
QuotientInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.MultiplyInteger)
RemainderInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.RemainderInteger)
ModInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.ModInteger)
EqualsInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.EqualsInteger)
LessThanInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.LessThanInteger)
LessThanEqualsInteger = wrap_builtin_binop(uplc_ast.BuiltInFun.LessThanEqualsInteger)
AppendByteString = wrap_builtin_binop(uplc_ast.BuiltInFun.AppendByteString)
ConsByteString = wrap_builtin_binop(uplc_ast.BuiltInFun.ConsByteString)
SliceByteString = wrap_builtin_ternop(uplc_ast.BuiltInFun.SliceByteString)
LengthOfByteString = wrap_builtin_unop(uplc_ast.BuiltInFun.LengthOfByteString)
IndexByteString = wrap_builtin_binop(uplc_ast.BuiltInFun.IndexByteString)
EqualsByteString = wrap_builtin_binop(uplc_ast.BuiltInFun.EqualsByteString)
LessThanByteString = wrap_builtin_binop(uplc_ast.BuiltInFun.LessThanByteString)
LessThanEqualsByteString = wrap_builtin_binop(
    uplc_ast.BuiltInFun.LessThanEqualsByteString
)
Sha2_256 = wrap_builtin_unop(uplc_ast.BuiltInFun.Sha2_256)
Sha3_256 = wrap_builtin_unop(uplc_ast.BuiltInFun.Sha3_256)
Blake2b_256 = wrap_builtin_unop(uplc_ast.BuiltInFun.Blake2b_256)
VerifySignature = wrap_builtin_ternop(uplc_ast.BuiltInFun.VerifyEd25519Signature)
VerifyEd25519Signature = wrap_builtin_ternop(uplc_ast.BuiltInFun.VerifyEd25519Signature)
VerifyEcdsaSecp256k1Signature = wrap_builtin_ternop(
    uplc_ast.BuiltInFun.VerifyEcdsaSecp256k1Signature
)
VerifySchnorrSecp256k1Signature = wrap_builtin_ternop(
    uplc_ast.BuiltInFun.VerifySchnorrSecp256k1Signature
)
AppendString = wrap_builtin_binop(uplc_ast.BuiltInFun.AppendString)
EqualsString = wrap_builtin_binop(uplc_ast.BuiltInFun.EqualsString)
EncodeUtf8 = wrap_builtin_unop(uplc_ast.BuiltInFun.EncodeUtf8)
DecodeUtf8 = wrap_builtin_unop(uplc_ast.BuiltInFun.DecodeUtf8)
# Note: prefer using Ite
IfThenElse = wrap_builtin_ternop_force(uplc_ast.BuiltInFun.IfThenElse)
ChooseUnit = wrap_builtin_unop_force(uplc_ast.BuiltInFun.ChooseUnit)
Trace = wrap_builtin_binop_force(uplc_ast.BuiltInFun.Trace)
FstPair = wrap_builtin_unop_force_force(uplc_ast.BuiltInFun.FstPair)
SndPair = wrap_builtin_unop_force_force(uplc_ast.BuiltInFun.SndPair)
ChooseList = wrap_builtin_ternop_force_force(uplc_ast.BuiltInFun.ChooseList)
MkCons = wrap_builtin_binop_force(uplc_ast.BuiltInFun.MkCons)
HeadList = wrap_builtin_unop_force(uplc_ast.BuiltInFun.HeadList)
TailList = wrap_builtin_unop_force(uplc_ast.BuiltInFun.TailList)
NullList = wrap_builtin_unop_force(uplc_ast.BuiltInFun.NullList)
ChooseData = wrap_builtin_hexop_force(uplc_ast.BuiltInFun.ChooseData)
ConstrData = wrap_builtin_binop(uplc_ast.BuiltInFun.ConstrData)
MapData = wrap_builtin_unop(uplc_ast.BuiltInFun.MapData)
ListData = wrap_builtin_unop(uplc_ast.BuiltInFun.ListData)
IData = wrap_builtin_unop(uplc_ast.BuiltInFun.IData)
BData = wrap_builtin_unop(uplc_ast.BuiltInFun.BData)
UnConstrData = wrap_builtin_unop(uplc_ast.BuiltInFun.UnConstrData)
UnMapData = wrap_builtin_unop(uplc_ast.BuiltInFun.UnMapData)
UnListData = wrap_builtin_unop(uplc_ast.BuiltInFun.UnListData)
UnIData = wrap_builtin_unop(uplc_ast.BuiltInFun.UnIData)
UnBData = wrap_builtin_unop(uplc_ast.BuiltInFun.UnBData)
EqualsData = wrap_builtin_binop(uplc_ast.BuiltInFun.EqualsData)
MkPairData = wrap_builtin_binop(uplc_ast.BuiltInFun.MkPairData)
MkNilData = wrap_builtin_unop(uplc_ast.BuiltInFun.MkNilData)
MkNilPairData = wrap_builtin_unop(uplc_ast.BuiltInFun.MkNilPairData)
SerialiseData = wrap_builtin_unop(uplc_ast.BuiltInFun.SerialiseData)

# Generic Utils


def TraceConst(x: AST, y: AST):
    return Trace(Text(x), y)


def TraceError(x: AST):
    return Apply(Error(), Trace(Text(x), Unit()))


@dataclass
class NotEqualsInteger(Pattern):
    a: AST
    b: AST

    def compose(self):
        return Not(EqualsInteger(self.a, self.b))


@dataclass
class Negate(Pattern):
    a: AST

    def compose(self):
        return SubtractInteger(Integer(0), self.a)


EqualsBool = Iff


# List Utils
@dataclass()
class EmptyList(AST):
    sample_value: uplc_ast.Constant
    _fields = []

    def compile(self) -> uplc_ast.AST:
        return uplc_ast.BuiltinList([], self.sample_value)

    def mk_nil_suffix(self):
        if isinstance(self.sample_value, uplc_ast.BuiltinPair):
            return f"Pair<{EmptyList(self.sample_value.l_value).mk_nil_suffix()}|{EmptyList(self.sample_value.r_value).mk_nil_suffix()}>"
        if isinstance(self.sample_value, uplc_ast.BuiltinList):
            return f"List{EmptyList(self.sample_value.sample_value).mk_nil_suffix()}"
        return self.sample_value.__class__.__name__

    def dumps(self) -> str:
        # Note: this is not a real builtin. Essentially, this is not pluto
        return f"MkNil{self.mk_nil_suffix()} ()"


def EmptyIntegerList():
    return EmptyList(uplc_ast.BuiltinInteger(0))


def EmptyByteStringList():
    return EmptyList(uplc_ast.BuiltinByteString(b""))


def EmptyTextList():
    return EmptyList(uplc_ast.BuiltinString(""))


def EmptyBoolList():
    return EmptyList(uplc_ast.BuiltinBool(False))


def EmptyUnitList():
    return EmptyList(uplc_ast.BuiltinUnit())


def EmptyListList(sample_value: uplc_ast.BuiltinList):
    return EmptyList(sample_value)


def EmptyPairList(sample_value: uplc_ast.BuiltinPair):
    return EmptyList(sample_value)


def EmptyDataList():
    # Create an empty list
    return MkNilData(Unit())


def EmptyDataPairList():
    # Create an empty list of pair type
    return MkNilPairData(Unit())


def IteNullList(lst: AST, i: AST, e: AST):
    """Ite based on whether a list is empty or not, choose over Ite(NullList(l), i, e) for performance reasons"""
    # Careful: can not patternize due to use of delay/force
    return Force(
        ChooseList(
            lst,
            Delay(i),
            Delay(e),
        )
    )


# Prepend an element to a list
PrependList = MkCons


@dataclass
class SingleDataList(Pattern):
    x: AST

    def compose(self):
        return PrependList(self.x, EmptyDataList())


@dataclass
class SingleDataPairList(Pattern):
    x: AST

    def compose(self):
        return PrependList(self.x, EmptyDataPairList())


@dataclass
class FoldList(Pattern):
    """Left fold over a list l operator f: accumulator -> list_elem -> accumulator with initial value a"""

    lst: AST
    f: AST
    a: AST

    def compose(self):
        return Apply(
            PLambda(
                ["op"],
                RecFun(
                    PLambda(
                        ["fold", "xs", "a"],
                        IteNullList(
                            PVar("xs"),
                            PVar("a"),
                            Apply(
                                PVar("fold"),
                                PVar("fold"),
                                TailList(PVar("xs")),
                                Apply(PVar("op"), PVar("a"), HeadList(PVar("xs"))),
                            ),
                        ),
                    ),
                ),
            ),
            self.f,
            self.lst,
            self.a,
        )


@dataclass
class RFoldList(Pattern):
    """Right fold over a list l operator f: accumulator -> list_elem -> accumulator with initial value a"""

    lst: AST
    f: AST
    a: AST

    def compose(self):
        return Apply(
            PLambda(
                ["op"],
                RecFun(
                    PLambda(
                        ["fold", "xs", "a"],
                        IteNullList(
                            PVar("xs"),
                            PVar("a"),
                            Apply(
                                PVar("op"),
                                Apply(
                                    PVar("fold"),
                                    PVar("fold"),
                                    TailList(PVar("xs")),
                                    PVar("a"),
                                ),
                                HeadList(PVar("xs")),
                            ),
                        ),
                    ),
                ),
            ),
            self.f,
            self.lst,
            self.a,
        )


_CONSTANT_INDEX_ACCESS_PATTERNS = {}
_CONSTANT_INDEX_ACCESS_PATTERNS_FAST = {}


def _NthConstantIndexAccessList(i: int):
    if i < 0:
        raise ValueError("Index must be non-negative")
    if _CONSTANT_INDEX_ACCESS_PATTERNS.get(i) is None:

        def assign_vars(self, lst: AST):
            self.lst = lst

        if i == 0:

            def compose(self):
                return Apply(
                    PLambda(
                        ["xs"],
                        IteNullList(
                            PVar("xs"), TraceError("IndexError"), HeadList(PVar("xs"))
                        ),
                    ),
                    self.lst,
                )

        else:

            def compose(self):
                return _NthConstantIndexAccessList(i - 1)(
                    Apply(
                        PLambda(
                            ["xs"],
                            IteNullList(
                                PVar("xs"),
                                TraceError("IndexError"),
                                TailList(PVar("xs")),
                            ),
                        ),
                        self.lst,
                    )
                )

        ConstantIndexAccessListPattern = type(
            f"ConstantIndexAccessListPattern_{i}",
            (Pattern,),
            {
                "__annotations__": {"lst": AST},
                "__init__": assign_vars,
                "compose": compose,
            },
        )
        ConstantIndexAccessListPattern = dataclass(ConstantIndexAccessListPattern)
        _CONSTANT_INDEX_ACCESS_PATTERNS[i] = ConstantIndexAccessListPattern
    return _CONSTANT_INDEX_ACCESS_PATTERNS[i]


def ConstantIndexAccessList(lst: AST, i: int):
    return _NthConstantIndexAccessList(i)(lst)


def _NthConstantIndexAccessListFast(i: int):
    if i < 0:
        raise ValueError("Index must be non-negative")
    if _CONSTANT_INDEX_ACCESS_PATTERNS_FAST.get(i) is None:

        def assign_vars(self, lst: AST):
            self.lst = lst

        if i == 0:

            def compose(self):
                return HeadList(self.lst)

        else:

            def compose(self):
                return _NthConstantIndexAccessListFast(i - 1)(TailList(self.lst))

        ConstantIndexAccessListPatternFast = type(
            f"ConstantIndexAccessListPatternFast_{i}",
            (Pattern,),
            {
                "__annotations__": {"lst": AST},
                "__init__": assign_vars,
                "compose": compose,
            },
        )
        ConstantIndexAccessListPatternFast = dataclass(
            ConstantIndexAccessListPatternFast
        )
        _CONSTANT_INDEX_ACCESS_PATTERNS_FAST[i] = ConstantIndexAccessListPatternFast
    return _CONSTANT_INDEX_ACCESS_PATTERNS_FAST[i]


def ConstantIndexAccessListFast(lst: AST, i: int):
    return _NthConstantIndexAccessListFast(i)(lst)


@dataclass
class IndexAccessList(Pattern):
    lst: AST
    i: AST

    def compose(self):
        return Apply(
            RecFun(
                PLambda(
                    ["f", "i", "xs"],
                    IteNullList(
                        PVar("xs"),
                        TraceError("IndexError"),
                        Ite(
                            EqualsInteger(PVar("i"), Integer(0)),
                            HeadList(PVar("xs")),
                            Apply(
                                PVar("f"),
                                PVar("f"),
                                SubtractInteger(PVar("i"), Integer(1)),
                                TailList(PVar("xs")),
                            ),
                        ),
                    ),
                ),
            ),
            self.i,
            self.lst,
        )


def n_times_taillist(a: AST, n: int):
    res = a
    for _ in range(n):
        res = TailList(res)
    return res


def IndexAccessListFast(step_size: int = 5):
    """
    Construct a pattern for step-size skip access
    """

    def compose(self):
        return Apply(
            PLet(
                [
                    (
                        "step_access",
                        RecFun(
                            PLambda(
                                ["f", "i", "xs"],
                                Ite(
                                    EqualsInteger(PVar("i"), Integer(0)),
                                    HeadList(PVar("xs")),
                                    Apply(
                                        PVar("f"),
                                        PVar("f"),
                                        SubtractInteger(PVar("i"), Integer(1)),
                                        TailList(PVar("xs")),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    (
                        "skip_access",
                        RecFun(
                            PLambda(
                                ["f", "i", "xs"],
                                Ite(
                                    LessThanInteger(PVar("i"), Integer(step_size)),
                                    Apply(PVar("step_access"), PVar("i"), PVar("xs")),
                                    Apply(
                                        PVar("f"),
                                        PVar("f"),
                                        SubtractInteger(PVar("i"), Integer(step_size)),
                                        n_times_taillist(PVar("xs"), step_size),
                                    ),
                                ),
                            )
                        ),
                    ),
                ],
                Apply(PVar("skip_access"), self.i, self.lst),
            )
        )

    def assign_vars(self, lst: AST, i: AST):
        self.lst = lst
        self.i = i

    IndexAccessListFastType = type(
        f"IndexAccessListFastType_{step_size}",
        (Pattern,),
        {
            "__annotations__": {"lst": AST, "i": AST},
            "__init__": assign_vars,
            "compose": compose,
        },
    )
    IndexAccessListFastType = dataclass(IndexAccessListFastType)

    return IndexAccessListFastType


@dataclass
class Range(Pattern):
    limit: AST
    start: AST = field(default_factory=lambda: Integer(0))
    step: AST = field(default_factory=lambda: Integer(1))

    def compose(self):
        return Apply(
            PLambda(
                ["limit", "step"],
                RecFun(
                    PLambda(
                        ["f", "cur"],
                        Ite(
                            LessThanInteger(PVar("cur"), PVar("limit")),
                            PrependList(
                                PVar("cur"),
                                Apply(
                                    PVar("f"),
                                    PVar("f"),
                                    AddInteger(PVar("cur"), PVar("step")),
                                ),
                            ),
                            EmptyIntegerList(),
                        ),
                    )
                ),
            ),
            self.limit,
            self.step,
            self.start,
        )


@dataclass
class MapList(Pattern):
    """Apply a map function on each element in a list"""

    lst: AST
    m: AST = field(default_factory=lambda: PLambda(["x"], PVar("x")))
    empty_list: AST = field(default_factory=EmptyDataList)

    def compose(self):
        return Apply(
            PLambda(
                ["op"],
                RecFun(
                    PLambda(
                        ["map", "xs"],
                        IteNullList(
                            PVar("xs"),
                            self.empty_list,
                            PrependList(
                                Apply(PVar("op"), HeadList(PVar("xs"))),
                                Apply(
                                    PVar("map"),
                                    PVar("map"),
                                    TailList(PVar("xs")),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            self.m,
            self.lst,
        )


@dataclass
class FindList(Pattern):
    """Returns the first element in the list where key evaluates to true - otherwise returns default"""

    lst: AST
    key: AST
    default: AST

    def compose(self):
        return Apply(
            PLambda(
                ["op"],
                RecFun(
                    PLambda(
                        ["f", "xs"],
                        IteNullList(
                            PVar("xs"),
                            self.default,
                            Ite(
                                Apply(PVar("op"), HeadList(PVar("xs"))),
                                HeadList(PVar("xs")),
                                Apply(
                                    PVar("f"),
                                    PVar("f"),
                                    TailList(PVar("xs")),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            self.key,
            self.lst,
        )


@dataclass
class AnyList(Pattern):
    """Returns whether the key evaluates to true anywhere in the list"""

    lst: AST
    key: AST

    def compose(self):
        return Apply(
            PLambda(
                ["op"],
                RecFun(
                    PLambda(
                        ["f", "xs"],
                        IteNullList(
                            PVar("xs"),
                            Bool(False),
                            Ite(
                                Apply(PVar("op"), HeadList(PVar("xs"))),
                                Bool(True),
                                Apply(
                                    PVar("f"),
                                    PVar("f"),
                                    TailList(PVar("xs")),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            self.key,
            self.lst,
        )


@dataclass
class AllList(Pattern):
    """Returns whether the key evaluates to true everywhere in the list"""

    lst: AST
    key: AST

    def compose(self):
        return Apply(
            PLambda(
                ["op"],
                RecFun(
                    PLambda(
                        ["f", "xs"],
                        IteNullList(
                            PVar("xs"),
                            Bool(True),
                            Ite(
                                Apply(PVar("op"), HeadList(PVar("xs"))),
                                Apply(
                                    PVar("f"),
                                    PVar("f"),
                                    TailList(PVar("xs")),
                                ),
                                Bool(False),
                            ),
                        ),
                    ),
                ),
            ),
            self.key,
            self.lst,
        )


@dataclass
class FilterList(Pattern):
    """Apply a filter function on each element in a list (throws out all that evaluate to false)"""

    lst: AST
    k: AST
    empty_list: AST = field(default_factory=EmptyDataList)

    def compose(self):
        return Apply(
            PLambda(
                ["op"],
                RecFun(
                    PLambda(
                        ["filter", "xs"],
                        IteNullList(
                            PVar("xs"),
                            self.empty_list,
                            PLet(
                                [("head", HeadList(PVar("xs")))],
                                Ite(
                                    Apply(PVar("op"), PVar("head")),
                                    PrependList(
                                        PVar("head"),
                                        Apply(
                                            PVar("filter"),
                                            PVar("filter"),
                                            TailList(PVar("xs")),
                                        ),
                                    ),
                                    Apply(
                                        PVar("filter"),
                                        PVar("filter"),
                                        TailList(PVar("xs")),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            self.k,
            self.lst,
        )


@dataclass
class MapFilterList(Pattern):
    """
    Apply a filter and a map function on each element in a list (throws out all that evaluate to false)
    Performs only a single pass and is hence much more efficient than filter + map
    """

    lst: AST
    filter_op: AST
    map_op: AST
    empty_list: AST = field(default_factory=EmptyDataList)

    def compose(self):
        return Apply(
            PLambda(
                ["filter", "map"],
                RecFun(
                    PLambda(
                        ["filtermap", "xs"],
                        IteNullList(
                            PVar("xs"),
                            self.empty_list,
                            PLet(
                                [("head", HeadList(PVar("xs")))],
                                Ite(
                                    Apply(PVar("filter"), PVar("head")),
                                    PrependList(
                                        Apply(PVar("map"), PVar("head")),
                                        Apply(
                                            PVar("filtermap"),
                                            PVar("filtermap"),
                                            TailList(PVar("xs")),
                                        ),
                                    ),
                                    Apply(
                                        PVar("filtermap"),
                                        PVar("filtermap"),
                                        TailList(PVar("xs")),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            self.filter_op,
            self.map_op,
            self.lst,
        )


@dataclass
class LengthList(Pattern):
    lst: AST

    def compose(self):
        return FoldList(
            self.lst, PLambda(["a", "_"], AddInteger(PVar("a"), Integer(1))), Integer(0)
        )


@dataclass
class TakeList(Pattern):
    """Take the first n elements of list l"""

    lst: AST
    n: AST
    empty_list: AST = field(default_factory=EmptyDataList)

    def compose(self):
        return Apply(
            RecFun(
                PLambda(
                    ["take", "xs", "n"],
                    IteNullList(
                        PVar("xs"),
                        self.empty_list,
                        Ite(
                            LessThanEqualsInteger(PVar("n"), Integer(0)),
                            self.empty_list,
                            PrependList(
                                HeadList(PVar("xs")),
                                Apply(
                                    PVar("take"),
                                    PVar("take"),
                                    TailList(PVar("xs")),
                                    SubtractInteger(PVar("n"), Integer(1)),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            self.lst,
            self.n,
        )


@dataclass
class DropList(Pattern):
    """Drop the first n elements of list l"""

    lst: AST
    n: AST
    empty_list: AST = field(default_factory=EmptyDataList)

    def compose(self):
        return Apply(
            RecFun(
                PLambda(
                    ["drop", "xs", "n"],
                    IteNullList(
                        PVar("xs"),
                        self.empty_list,
                        Ite(
                            LessThanEqualsInteger(PVar("n"), Integer(0)),
                            PVar("xs"),
                            Apply(
                                PVar("drop"),
                                PVar("drop"),
                                TailList(PVar("xs")),
                                SubtractInteger(PVar("n"), Integer(1)),
                            ),
                        ),
                    ),
                ),
            ),
            self.lst,
            self.n,
        )


@dataclass
class SliceList(Pattern):
    """Drop the first i elements of list l and take the remaining j elements"""

    i: AST
    j: AST
    lst: AST
    empty_list: AST = field(default_factory=EmptyDataList)

    def compose(self):
        return TakeList(
            DropList(self.lst, self.i, self.empty_list), self.j, self.empty_list
        )


# Data Utils


@dataclass
class Constructor(Pattern):
    d: AST

    def compose(self):
        return FstPair(UnConstrData(self.d))


@dataclass
class Fields(Pattern):
    d: AST

    def compose(self):
        return SndPair(UnConstrData(self.d))


@dataclass
class NthField(Pattern):
    d: AST
    n: AST

    def compose(self):
        return IndexAccessList(Fields(self.d), self.n)


def ConstantNthField(d: AST, i: int):
    return ConstantIndexAccessList(Fields(d), i)


def ConstantNthFieldFast(d: AST, i: int):
    return ConstantIndexAccessListFast(Fields(d), i)


@dataclass
class NoneData(Pattern):
    def compose(self):
        return ConstrData(Integer(0), EmptyDataList())


@dataclass
class SomeData(Pattern):
    x: AST
    # Note: x must be of type data!

    def compose(self):
        return ConstrData(Integer(1), SingleDataList(self.x))


# Choose Utils


def DelayedChooseData(
    d: AST,
    constr_branch: AST,
    map_branch: AST,
    list_branch: AST,
    int_branch: AST,
    bytestring_branch: AST,
):
    # Careful: cannot patternize because of delay/force
    return Force(
        ChooseData(
            d,
            Delay(constr_branch),
            Delay(map_branch),
            Delay(list_branch),
            Delay(int_branch),
            Delay(bytestring_branch),
        )
    )


# concatenation utils


def _concat(append, empty):
    def f(*ss: typing.List[AST]):
        if not ss:
            return empty
        c = ss[-1]
        for s in reversed(ss[:-1]):
            c = append(s, c)
        return c

    return f


@dataclass
class AppendList(Pattern):
    xs: AST
    ys: AST

    def compose(self):
        return Apply(
            RecFun(
                PLambda(
                    ["append", "xs", "ys"],
                    IteNullList(
                        PVar("xs"),
                        PVar("ys"),
                        PrependList(
                            HeadList(PVar("xs")),
                            Apply(
                                PVar("append"),
                                PVar("append"),
                                TailList(PVar("xs")),
                                PVar("ys"),
                            ),
                        ),
                    ),
                )
            ),
            self.xs,
            self.ys,
        )


ConcatString = _concat(AppendString, Text(""))
ConcatByteString = _concat(AppendByteString, ByteString(b""))


def ConcatList(sample_value: uplc_ast.Constant):
    return _concat(AppendList, EmptyList(sample_value))

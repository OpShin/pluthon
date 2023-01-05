from uplc import uplc_ast
from .pluthon_ast import *

########## Pluto Abstractions that simplify handling complex structures ####################


def Not(x: AST):
    return Ite(x, Bool(False), Bool(True))


def Iff(x: AST, y: AST):
    return Ite(x, y, Not(y))


def wrap_builtin_binop(b: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST):
        return Apply(b, x, y)

    return wrapped


def wrap_builtin_binop_force(b: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST):
        return Apply(Force(b), x, y)

    return wrapped


def wrap_builtin_binop_force_force(b: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST):
        return Apply(Force(Force(b)), x, y)

    return wrapped


def wrap_builtin_ternop(t: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST, z: AST):
        return Apply(t, x, y, z)

    return wrapped


def wrap_builtin_ternop_force_force(t: uplc_ast.BuiltInFun):
    def wrapped(x: AST, y: AST, z: AST):
        return Apply(Force(Force(t)), x, y, z)

    return wrapped


def wrap_builtin_unop(u: uplc_ast.BuiltInFun):
    def wrapped(x: AST):
        return Apply(u, x)

    return wrapped


def wrap_builtin_unop_force(u: uplc_ast.BuiltInFun):
    def wrapped(x: AST):
        return Apply(Force(u), x)

    return wrapped


def wrap_builtin_unop_force_force(u: uplc_ast.BuiltInFun):
    def wrapped(x: AST):
        return Apply(Force(Force(u)), x)

    return wrapped


def wrap_builtin_hexop_force(u: uplc_ast.BuiltInFun):
    def wrapped(d: AST, v: AST, w: AST, x: AST, y: AST, z: AST):
        return Apply(Force(u), d, v, w, x, y, z)

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
VerifySignature = wrap_builtin_unop(uplc_ast.BuiltInFun.VerifySignature)
AppendString = wrap_builtin_binop(uplc_ast.BuiltInFun.AppendString)
EqualsString = wrap_builtin_binop(uplc_ast.BuiltInFun.EqualsString)
EncodeUtf8 = wrap_builtin_unop(uplc_ast.BuiltInFun.EncodeUtf8)
DecodeUtf8 = wrap_builtin_unop(uplc_ast.BuiltInFun.DecodeUtf8)
# Note: prefer using Ite
IfThenElse = wrap_builtin_unop_force(uplc_ast.BuiltInFun.IfThenElse)
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

# Generic Utils

TraceConst = lambda x, y: Trace(Text(x), y)


def NotEqualsInteger(a: AST, b: AST):
    return Not(EqualsInteger(a, b))


EqualsBool = Iff

# List Utils


def EmptyList():
    # Create an empty list
    return Apply(MkNilData, Unit())


def EmptyPairList():
    # Create an empty list of pair type
    return Apply(MkNilPairData, Unit())


# Prepend an element to a list
PrependList = MkCons


def SingleList(x: AST):
    return PrependList(x, EmptyList())


def IndexAccessList(l: AST, i: AST):
    return Let(
        [
            (
                "g",
                Lambda(
                    ["i", "xs", "f"],
                    Ite(
                        NullList(Var("xs")),
                        TraceConst("IndexError", Error()),
                        Ite(
                            EqualsInteger(Var("i"), Integer(0)),
                            HeadList(Var("xs")),
                            Apply(
                                Var("f"),
                                SubtractInteger(Var("i"), Integer(1)),
                                TailList(Var("xs")),
                                Var("f"),
                            ),
                        ),
                    ),
                ),
            )
        ],
        Apply(
            Var("g"),
            l,
            i,
            Var("g"),
        ),
    )


# Data Utils


def Constructor(d: AST):
    return Apply(
        Force(Force(BuiltIn(uplc_ast.BuiltInFun.FstPair))),
        Apply(BuiltIn(uplc_ast.BuiltInFun.UnConstrData), d),
    )


def Fields(d: AST):
    return Apply(
        Force(Force(BuiltIn(uplc_ast.BuiltInFun.SndPair))),
        Apply(BuiltIn(uplc_ast.BuiltInFun.UnConstrData), d),
    )


def NthField(d: AST, n: AST):
    return IndexAccessList(Fields(d), n)


def NoneData():
    return ConstrData(Integer(0), EmptyList())


def SomeData(x: AST):
    # Note: x must be of type data!
    return ConstrData(Integer(1), SingleList(x))

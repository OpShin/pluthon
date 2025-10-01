from dataclasses import dataclass
import typing

from uplc import ast as uplc_ast, eval as uplc_eval


@dataclass
class AST:
    def compile(self) -> uplc_ast.AST:
        raise NotImplementedError()

    def dumps(self) -> str:
        raise NotImplementedError()

    def eval(self) -> str:
        return uplc_eval(self.compile())


@dataclass
class Program(AST):
    version: typing.Tuple[int, int, int]
    prog: AST

    def compile(self):
        return uplc_ast.Program(self.version, self.prog.compile())

    def dumps(self) -> str:
        # There is no equivalent in "pure" pluto
        return self.prog.dumps()


@dataclass
class Var(AST):
    name: str

    def compile(self):
        return uplc_ast.Variable(self.name)

    def dumps(self) -> str:
        return self.name


@dataclass
class Lambda(AST):
    vars: typing.List[str]
    term: AST

    def compile(self):
        if not self.vars:
            raise RuntimeError("Invalid lambda without variables")
        t = self.term.compile()
        varscp = self.vars.copy()
        while varscp:
            t = uplc_ast.Lambda(varscp.pop(), t)
        return t

    def dumps(self) -> str:
        return f"(\\{' '.join(self.vars)} -> {self.term.dumps()})"


@dataclass
class Apply(AST):
    f: AST
    xs: typing.List[AST]

    def __init__(self, f: AST, *xs: AST) -> None:
        super().__init__()
        self.f = f
        self.xs = xs

    def compile(self):
        f = self.f.compile()
        for x in self.xs:
            f = uplc_ast.Apply(f, x.compile())
        return f

    def dumps(self) -> str:
        return f"({self.f.dumps()} {' '.join(x.dumps() for x in self.xs)})"


@dataclass
class Force(AST):
    x: AST

    def compile(self):
        return uplc_ast.Force(self.x.compile())

    def dumps(self) -> str:
        return f"(! {self.x.dumps()})"


@dataclass
class Delay(AST):
    x: AST

    def compile(self):
        return uplc_ast.Delay(self.x.compile())

    def dumps(self) -> str:
        return f"(# {self.x.dumps()})"


@dataclass
class Integer(AST):
    x: int

    def compile(self):
        return uplc_ast.BuiltinInteger(self.x)

    def dumps(self) -> str:
        return str(self.x)


@dataclass
class ByteString(AST):
    x: bytes

    def compile(self):
        return uplc_ast.BuiltinByteString(self.x)

    def dumps(self) -> str:
        return f"0x{self.x.hex()}"


@dataclass
class Text(AST):
    x: str

    def compile(self):
        return uplc_ast.BuiltinString(self.x)

    def dumps(self) -> str:
        return repr(self.x)


@dataclass
class Bool(AST):
    x: bool

    def compile(self):
        return uplc_ast.BuiltinBool(self.x)

    def dumps(self) -> str:
        return "True" if self.x else "False"


@dataclass
class Unit(AST):
    def compile(self):
        return uplc_ast.BuiltinUnit()

    def dumps(self) -> str:
        return "()"


@dataclass
class UPLCConstant(AST):
    """
    A generic UPLC constant that can be written directly in pluthon
    Note: not present in pluthon
    """

    x: uplc_ast.Constant

    def compile(self):
        return self.x

    def dumps(self) -> str:
        return f"uplc[{self.x.dumps(dialect=uplc_ast.UPLCDialect.Plutus)}]"


@dataclass
class BuiltIn(AST):
    builtin: uplc_ast.BuiltInFun

    def compile(self):
        return uplc_ast.BuiltIn(self.builtin)

    def dumps(self) -> str:
        return f"{self.builtin.name}"


@dataclass
class Error(AST):
    def compile(self):
        # Wrap error such that it is never really executed
        return uplc_ast.Lambda("_", uplc_ast.Error())

    def dumps(self) -> str:
        return "Error"


@dataclass
class Let(AST):
    # NOTE: visitor needs to take care to correctly visit the bindings
    bindings: typing.List[typing.Tuple[str, AST]]
    term: AST

    def compile(self):
        t = self.term.compile()
        bindingscp = self.bindings.copy()
        while bindingscp:
            (b_name, b_term) = bindingscp.pop()
            t = uplc_ast.Apply(
                uplc_ast.Lambda(b_name, t),
                b_term.compile(),
            )
        return t

    def dumps(self) -> str:
        bindingss = ";".join(
            f"{b_name} = {b_term.dumps()}" for b_name, b_term in self.bindings
        )
        return f"(let {bindingss} in {self.term.dumps()})"


@dataclass
class Ite(AST):
    """
    If-then-else expression
    Executes t when i evaluates to true, otherwise e
    """

    i: AST
    t: AST
    e: AST

    def compile(self):
        return uplc_ast.Force(
            uplc_ast.Apply(
                uplc_ast.Apply(
                    uplc_ast.Apply(
                        uplc_ast.Force(
                            uplc_ast.BuiltIn(uplc_ast.BuiltInFun.IfThenElse)
                        ),
                        self.i.compile(),
                    ),
                    uplc_ast.Delay(self.t.compile()),
                ),
                uplc_ast.Delay(self.e.compile()),
            )
        )

    def dumps(self) -> str:
        return f"(if {self.i.dumps()} then {self.t.dumps()} else {self.e.dumps()})"


@dataclass
class Pattern(AST):
    """Marks a more abstract pattern that can be shrinked by the compiler by reusage"""

    def compose(self):
        """Composes the variables to a pluto pattern"""
        raise NotImplementedError()

    def compile(self):
        return self.compose().compile()

    def dumps(self) -> str:
        return f"<[{self.__class__.__name__}]> {self.compose().dumps()}"

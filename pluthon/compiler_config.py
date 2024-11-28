from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CompilationConfig:
    compress_patterns: Optional[bool] = None
    iterative_unfold_patterns: Optional[bool] = None
    constant_index_access_list: Optional[bool] = None

    def update(
        self, other: Optional["CompilationConfig"] = None, **kwargs
    ) -> "CompilationConfig":
        own_dict = self.__dict__
        other_dict = other.__dict__ if isinstance(other, CompilationConfig) else kwargs
        return self.__class__(
            **{
                k: other_dict.get(k) if other_dict.get(k) is not None else own_dict[k]
                for k in set(own_dict.keys()) | set(other_dict.keys())
            }
        )


# The default configuration for the compiler
OPT_O0_CONFIG = CompilationConfig(
    compress_patterns=False,
    iterative_unfold_patterns=False,
)
OPT_O1_CONFIG = OPT_O0_CONFIG.update(
    compress_patterns=True,
    constant_index_access_list=True,
)
OPT_O2_CONFIG = OPT_O1_CONFIG.update()
OPT_O3_CONFIG = OPT_O2_CONFIG.update(
    iterative_unfold_patterns=True,
)
OPT_CONFIGS = [OPT_O0_CONFIG, OPT_O1_CONFIG, OPT_O2_CONFIG, OPT_O3_CONFIG]

DEFAULT_CONFIG = CompilationConfig().update(OPT_O1_CONFIG)

ARGPARSE_ARGS = {
    "compress_patterns": {
        "help": "Enables the compression of re-occurring code patterns. Can reduce memory and CPU steps but increases the size of the compiled contract.",
    },
    "iterative_unfold_patterns": {
        "help": "Enables iterative unfolding of patterns. Improves application of pattern optimization but is very slow.",
    },
    "constant_index_access_list": {
        "help": "Replace index accesses with constant parameters with optimized constant accesses. Can reduce memory and CPU steps but increases the size of the compiled contract.",
    },
}
for k in ARGPARSE_ARGS:
    assert (
        k in DEFAULT_CONFIG.__dict__
    ), f"Key {k} not found in CompilationConfig.__dict__"

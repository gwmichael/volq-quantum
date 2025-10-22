from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["backend", "frontend", "Circuit"]

# Allow type checkers to see names without runtime import
if TYPE_CHECKING:  # pragma: no cover - static typing only
    from .backend.quantum_circuit import Circuit  # type: ignore

# cache loaded attributes to avoid re-importing repeatedly
__loaded_cache = {}

def __getattr__(name: str):
    # lazy-load the requested attribute
    if name in __loaded_cache:
        return __loaded_cache[name]

    if name == "Circuit":
        mod = import_module("volq.backend.quantum_circuit")
        value = getattr(mod, "Circuit")
    elif name == "backend":
        value = import_module("volq.backend")
    elif name == "frontend":
        value = import_module("volq.frontend")
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    __loaded_cache[name] = value
    return value

def __dir__():
    return sorted(list(globals().keys()) + __all__)

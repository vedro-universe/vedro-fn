from functools import wraps
from typing import Any, Callable, Optional, Sequence, Tuple

from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("scenario",)


class scenario:
    def __init__(self, params: Optional[Sequence[Any]] = None, /) -> None:
        self._params: Tuple[Any, ...] = tuple(params) if params else ()
        self._decorators: Tuple[Callable[..., Any], ...] = ()

    def __call__(self, fn: Callable[..., Any]) -> ScenarioDescriptor:
        return ScenarioDescriptor(fn, self._decorators, self._params)

    def __class_getitem__(cls, item: Any) -> Callable[..., "scenario"]:
        decorators = item if isinstance(item, tuple) else (item,)

        @wraps(scenario)
        def wrapped(params: Optional[Sequence[Any]] = None, /) -> "scenario":
            scn = scenario(params)
            scn._decorators = decorators
            return scn
        return wrapped

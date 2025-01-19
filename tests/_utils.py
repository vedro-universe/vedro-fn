import pytest
from vedro.core import Dispatcher

from vedro_fn import VedroFn, VedroFnPlugin

__all__ = ("dispatcher", "vedro_fn",)


@pytest.fixture
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture
def vedro_fn(dispatcher: Dispatcher) -> VedroFnPlugin:
    plugin = VedroFnPlugin(VedroFn)
    plugin.subscribe(dispatcher)
    return plugin

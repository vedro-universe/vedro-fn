import os
from pathlib import Path
from typing import List, Type

import pytest
from vedro import Scenario
from vedro.core import Dispatcher, ModuleFileLoader, Report, VirtualScenario
from vedro.core.scenario_discoverer import create_vscenario
from vedro.core.scenario_runner import MonotonicScenarioRunner as ScenarioRunner
from vedro.core.scenario_scheduler import MonotonicScenarioScheduler as ScenarioScheduler

from vedro_fn import VedroFn, VedroFnPlugin
from vedro_fn._scenario_loader import ScenarioLoader

__all__ = ("dispatcher", "vedro_fn", "tmp_scn_dir", "loader", "run_scenarios",)


@pytest.fixture
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture
def vedro_fn(dispatcher: Dispatcher) -> VedroFnPlugin:
    plugin = VedroFnPlugin(VedroFn)
    plugin.subscribe(dispatcher)
    return plugin


@pytest.fixture
def tmp_scn_dir(tmp_path: Path) -> Path:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        scn_dir = tmp_path / "scenarios/"
        scn_dir.mkdir(exist_ok=True)
        yield scn_dir.relative_to(tmp_path)
    finally:
        os.chdir(cwd)


@pytest.fixture
def loader() -> ScenarioLoader:
    return ScenarioLoader(ModuleFileLoader())


async def run_scenarios(scenarios: List[Type[Scenario]], dispatcher: Dispatcher, *,
                        project_dir: Path) -> Report:
    scenarios = [_create_vscenario(scn, project_dir=project_dir) for scn in scenarios]
    scheduler = ScenarioScheduler(scenarios)

    runner = ScenarioRunner(dispatcher)
    report = await runner.run(scheduler)
    return report


def _create_vscenario(scenario: Type[Scenario], *, project_dir: Path) -> VirtualScenario:
    vscenario = create_vscenario(scenario, project_dir=project_dir)

    template = getattr(scenario, "__vedro__template__", None)
    is_skipped = getattr(template, "__vedro__skipped__",
                         getattr(scenario, "__vedro__skipped__", False))
    if is_skipped:
        vscenario.skip()

    return vscenario

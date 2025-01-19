import os
from asyncio import iscoroutinefunction
from pathlib import Path
from types import ModuleType
from typing import List, Type

from vedro import Scenario
from vedro.core import ModuleLoader
from vedro.core import ScenarioLoader as BaseScenarioLoader

from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("ScenarioLoader",)


class ScenarioLoader(BaseScenarioLoader):
    def __init__(self, module_loader: ModuleLoader) -> None:
        self._module_loader = module_loader

    async def load(self, path: Path) -> List[Type[Scenario]]:
        module = await self._module_loader.load(path)
        return self._collect_scenarios(module)

    def _collect_scenarios(self, module: ModuleType) -> List[Type[Scenario]]:
        loaded = []
        for name, val in module.__dict__.items():
            if not name.startswith("_") and isinstance(val, ScenarioDescriptor):
                scenarios = self._build_vedro_scenarios(val, module)
                loaded.extend(scenarios)
        return loaded

    def _build_vedro_scenarios(self, descriptor: ScenarioDescriptor,
                               module: ModuleType) -> List[Type[Scenario]]:
        module_path = os.path.abspath(str(module.__file__))

        subject = descriptor.name.replace("_", " ")

        if len(descriptor.params) == 0:

            if iscoroutinefunction(descriptor.fn):
                async def do(self) -> None:  # type: ignore
                    await descriptor.fn()
            else:
                def do(self) -> None:  # type: ignore
                    descriptor.fn()

            cls_name = f"Scenario_{descriptor.name}"
            scenario = type(cls_name, (Scenario,), {
                "__file__": module_path,
                "subject": subject,
                "do": do,
            })

            for decorator in descriptor.decorators:
                scenario = decorator(scenario)

            return [scenario]

        else:
            return []

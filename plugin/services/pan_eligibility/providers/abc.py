from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plugin.models import Plugin

class AbstractPANEligibilityProvider(ABC):
    def __init__(self, plugin: "Plugin"):
        self.plugin = plugin

    @abstractmethod
    async def is_pan_eligible(self, plugin: "Plugin", pan_number: str) -> bool:
        pass

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..models import VehicleRCVerificationRequest, VehicleRCVerificationResponse

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractVehicleRCVerificationProvider(ABC):
    def __init__(self, plugin: "Plugin"):
        self.plugin = plugin

    @abstractmethod
    def run(
        self, plugin: "Plugin", request: VehicleRCVerificationRequest
    ) -> VehicleRCVerificationResponse:
        pass

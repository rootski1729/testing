from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..serializers import (
    MobileToVehicleRCRequestSerializer,
    MobileToVehicleRCResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractMobileToVehicleRCProvider(ABC):
    @abstractmethod
    def fetch_vehicle_rc(
        self, plugin: "Plugin", request: MobileToVehicleRCRequestSerializer
    ) -> MobileToVehicleRCResponseSerializer:
        pass

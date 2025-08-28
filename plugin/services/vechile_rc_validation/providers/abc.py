from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..vechile_rc_serializer import (VehicleRCVerificationRequestSerializer,
                                    VehicleRCVerificationResponseSerializer)

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractVehicleRCVerificationProvider(ABC):

    @abstractmethod
    def verify_rc(
        self, plugin: "Plugin", request: VehicleRCVerificationRequestSerializer
    ) -> VehicleRCVerificationResponseSerializer:
    
        pass

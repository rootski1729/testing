from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..serializers import (
    DrivingLicenseVerificationRequestSerializer,
    DrivingLicenseVerificationResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractDrivingLicenseVerificationProvider(ABC):
    @abstractmethod
    def verify_driving_license(
        self, plugin: "Plugin", request: DrivingLicenseVerificationRequestSerializer
    ) -> DrivingLicenseVerificationResponseSerializer:
        
        pass

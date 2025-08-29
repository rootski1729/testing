from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..models import (
    DrivingLicenseVerificationRequest,
    DrivingLicenseVerificationResponse,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractDrivingLicenseVerificationProvider(ABC):
    def __init__(self, plugin: "Plugin"):
        self.plugin = plugin
        
    @abstractmethod
    def verify_driving_license(
        self, plugin: "Plugin", request: DrivingLicenseVerificationRequest
    ) -> DrivingLicenseVerificationResponse:
        
        pass

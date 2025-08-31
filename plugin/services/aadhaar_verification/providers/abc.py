from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..models import (
    AadhaarOTPGenerateRequest,
    AadhaarOTPGenerateResponse,
    AadhaarOTPVerifyRequest,
    AadhaarVerificationResponse,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractAadhaarVerificationProvider(ABC):

    @abstractmethod
    def generate_otp(
        self, plugin: "Plugin", request: AadhaarOTPGenerateRequest
    ) -> AadhaarOTPGenerateResponse:
        pass

    @abstractmethod
    def verify_otp(
        self, plugin: "Plugin", request: AadhaarOTPVerifyRequest
    ) -> AadhaarVerificationResponse:

        pass

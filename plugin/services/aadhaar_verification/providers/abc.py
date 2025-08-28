from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..serializers import (
    AadhaarOTPGenerateRequestSerializer, AadhaarOTPGenerateResponseSerializer,
    AadhaarOTPVerifyRequestSerializer, AadhaarVerificationResponseSerializer
    
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractAadhaarVerificationProvider(ABC):
    """Abstract base class for Aadhaar verification providers - 2-step process"""
    
    @abstractmethod
    def generate_otp(self, plugin: "Plugin", request: AadhaarOTPGenerateRequestSerializer) -> AadhaarOTPGenerateResponseSerializer:
        
        pass
    
    @abstractmethod
    def verify_otp(self, plugin: "Plugin", request: AadhaarOTPVerifyRequestSerializer) -> AadhaarVerificationResponseSerializer:
        
        pass
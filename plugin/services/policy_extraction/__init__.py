from plugin.runner import ServiceRunner
from plugin.enums import PluginService
from .models import PolicyExtractionResponse, PolicyExtractionRequest

policy_extraction = ServiceRunner(PluginService.POLICY_EXTRACTION)
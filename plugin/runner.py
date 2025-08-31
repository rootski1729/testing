from plugin.models import Plugin
from plugin.enums import PluginService
from plugin.utils.plugin_factory import PluginFactory
from plugin.services.core.models.base import BasePluginResponse

class ServiceRunner():
    def __init__(self, service: PluginService):
        self.service = service

    def run(self, request, payload):
        company = request.user.company
        plugin = Plugin.objects.filter(company=company, service=self.service.value).first()
        if not plugin:
            return BasePluginResponse(is_success=False, message="No active plugin found.")

        provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
        provider = provider_class(plugin)
        return provider.run(plugin, payload)


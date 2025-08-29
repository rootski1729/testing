# plugin/utils/cache_mixin.py
import hashlib
import json
from typing import Dict, Any, Optional, TYPE_CHECKING
from django.conf import settings

if TYPE_CHECKING:
    from plugin.models import Plugin


class PluginCacheMixin:
    
    CACHE_EXPIRY_MINUTES = 60 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lazy import to avoid cycles
        from core.database.mongodb.services import MongoDB
        self.mongodb = MongoDB()
        self.mongodb.setup(settings.MONGODB_SETTINGS)

        try:
            self.mongodb.plugin_cache.create_index(
                "created_at",
                expireAfterSeconds=self.CACHE_EXPIRY_MINUTES * 60
            )
            self.mongodb.plugin_cache.create_index(
                [("plugin_uid", 1), ("service", 1), ("request_hash", 1)],
                name="plugin_service_request_hash",
                unique=True
            )
        except Exception as e:
            # don't break flow due to index errors
            print(f"[Cache] index ensure error: {e}")

    def get_service_name(self) -> str:
        raise NotImplementedError("Service must implement get_service_name()")

    def _generate_request_hash(self, request_data: Dict[str, Any]) -> str:
        sorted_data = json.dumps(request_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(sorted_data.encode("utf-8")).hexdigest()

    def get_cached_response(
        self, plugin: "Plugin", request_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            request_hash = self._generate_request_hash(request_data)
            query = {
                "plugin_uid": plugin.uid,
                "service": self.get_service_name(),
                "request_hash": request_hash,
            }
            doc = self.mongodb._find_one(self.mongodb.plugin_cache, query)
            if not doc:
                return None
            return doc.get("response_data")
        except Exception as e:
            print(f"[Cache] retrieval error: {e}")
            return None

    def cache_response(
        self, plugin: "Plugin", request_data: Dict[str, Any], raw_response: Dict[str, Any]
    ) -> bool:
        try:
            if raw_response.get("sub_code") != "SUCCESS":
                return False

            request_hash = self._generate_request_hash(request_data)
            doc = {
                "plugin_uid": plugin.uid,
                "service": self.get_service_name(),
                "provider": plugin.provider,
                "request_hash": request_hash,
                "request_data": request_data,
                "response_data": raw_response,   
                "created_at": self.mongodb.now(),
            }
            self.mongodb._update_one(
                self.mongodb.plugin_cache,
                {"plugin_uid": plugin.uid, "service": self.get_service_name(), "request_hash": request_hash},
                {"$set": doc},
                upsert=True,
            )
            return True
        except Exception as e:
            print(f"[Cache] storage error: {e}")
            return False

    def cached_request(
        self,
        plugin: "Plugin",
        request_data: Dict[str, Any],
        api_call_func,
    ) -> Dict[str, Any]:
        
        cached = self.get_cached_response(plugin, request_data)
        if cached:
            return cached

        raw = api_call_func()
        self.cache_response(plugin, request_data, raw)
        return raw

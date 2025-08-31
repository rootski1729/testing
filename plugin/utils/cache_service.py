# plugin/utils/cache_service.py
import hashlib
import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from django.conf import settings

from core.database import mongodb

if TYPE_CHECKING:
    from plugin.models import Plugin


class PluginCacheService:
    CACHE_EXPIRY_MINUTES = 60

    def __init__(self):
        self._ensure_indexes()

    def _ensure_indexes(self):
        mongodb.plugin_cache.create_index(
            "created_at", expireAfterSeconds=self.CACHE_EXPIRY_MINUTES * 60
        )
        mongodb.plugin_cache.create_index(
            [("plugin_uid", 1), ("service", 1), ("request_hash", 1)],
            name="plugin_service_request_hash",
            unique=True,
        )

    def _generate_request_hash(self, request_data: Dict[str, Any]) -> str:
        try:
            sorted_data = json.dumps(request_data, sort_keys=True, separators=(",", ":"))
            return hashlib.sha256(sorted_data.encode("utf-8")).hexdigest()
        except Exception as e: # TODO handle for file inputs
            return None

    def get_cached_response(
        self, plugin: "Plugin", service: str, request_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            request_hash = self._generate_request_hash(request_data)
            if not request_hash:
                return None
            query = {
                "plugin_uid": plugin.uid,
                "service": service,
                "request_hash": request_hash,
            }
            doc = mongodb.plugin_cache.find_one(query)
            return doc.get("response_data") if doc else None

        except MemoryError:
            return None

    def cache_response(
        self,
        plugin: "Plugin",
        service: str,
        request_data: Dict[str, Any],
        raw_response: Dict[str, Any],
    ) -> bool:
        """Cache successful response"""
        try:
            if not self._is_successful_response(raw_response):
                return False

            request_hash = self._generate_request_hash(request_data)
            doc = {
                "plugin_uid": plugin.uid,
                "service": service,
                "provider": plugin.provider,
                "request_hash": request_hash,
                "request_data": request_data,
                "response_data": raw_response,
                "created_at": datetime.utcnow(),
            }

            mongodb.plugin_cache.update_one(
                {
                    "plugin_uid": plugin.uid,
                    "service": service,
                    "request_hash": request_hash,
                },
                {"$set": doc},
                upsert=True,
            )
            return True
        except MemoryError:
            return False

    def _is_successful_response(self, response: Dict[str, Any]) -> bool:
        return (
            response.get("sub_code") == "SUCCESS"  # Deepvue
            or response.get("code") == 200  # HTTP success
            or response.get("success") is True  # General success flag
        )


cache_service = PluginCacheService()

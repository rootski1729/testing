from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from pydantic import BaseModel

from .cache_service import cache_service

if TYPE_CHECKING:
    from plugin.models import Plugin


def auto_cached_provider_method(
    exclude_fields: Optional[List[str]] = None, cache_disabled: bool = False
):

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, plugin: "Plugin", request: BaseModel, *args, **kwargs):

            if cache_disabled:
                return func(self, plugin, request, *args, **kwargs)

            service_name = plugin.service

            request_data = (
                request.model_dump()
                if hasattr(request, "model_dump")
                else request.dict()
            )

            cache_key_data = request_data.copy()
            if exclude_fields:
                for field in exclude_fields:
                    cache_key_data.pop(field, None)

            cached_response = cache_service.get_cached_response(
                plugin, service_name, cache_key_data
            )

            if cached_response:
                return_annotation = func.__annotations__.get("return")
                if return_annotation:
                    try:
                        return return_annotation(**cached_response)
                    except Exception:
                        pass

            response = func(self, plugin, request, *args, **kwargs)

            raw_response_data = (
                response.model_dump()
                if hasattr(response, "model_dump")
                else response.dict()
            )

            cache_service.cache_response(
                plugin, service_name, cache_key_data, raw_response_data
            )

            return response

        return wrapper

    return decorator


def simple_cached_provider_method(func: Callable) -> Callable:
    return auto_cached_provider_method()(func)

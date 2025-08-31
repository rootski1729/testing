from typing import List, Optional, Any

from pydantic import BaseModel, Field


class BasePluginResponse(BaseModel):
    request_id: Optional[str] = None
    is_success: bool
    message: str
    response: Optional[Any] = None

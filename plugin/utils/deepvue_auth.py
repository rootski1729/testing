import httpx
from typing import Optional, Dict, Any
import time


class DeepvueAuth:
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[int] = None

    def authenticate(self) -> bool:
        url = f"{self.BASE_URL}/v1/authorize"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            resp = httpx.post(url, data=data)
            resp.raise_for_status()
            body = resp.json()

            self._access_token = body.get("access_token")
            expiry = body.get("expiry")
            if expiry == "24hrs":
                self._token_expiry = int(time.time()) + (24 * 60 * 60)
            elif expiry and str(expiry).isdigit():
                self._token_expiry = int(time.time()) + int(expiry)
            else:
                self._token_expiry = int(time.time()) + (23 * 60 * 60)

            return True if self._access_token else False

        except Exception:
            return False

    def get_access_token(self) -> Optional[str]:
        if not self._access_token or (
            self._token_expiry and time.time() >= self._token_expiry
        ):
            success = self.authenticate()
            if not success:
                return None
        return self._access_token

    def make_request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        token = self.get_access_token()
        
        
        
        if not token:
            return {
                "success": False,
                "sub_code": "AUTH_FAILED",
                "message": "Authentication failed, no token received",
                "data": {}
            }

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "x-api-key": self.client_secret,
            "Content-Type": "application/json",
        }

        try:
            response = httpx.request(
                method, url, headers=headers, params=params, json=json
            )
            response.raise_for_status()
            result = response.json()
            return result

        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "sub_code": "HTTP_ERROR",
                "message": f"HTTP {e.response.status_code}: {e.response.text}",
                "data": {}
            }
        except Exception as e:
            return {
                "success": False,
                "sub_code": "REQUEST_FAILED",
                "message": f"Request failed: {str(e)}",
                "data": {}
            }

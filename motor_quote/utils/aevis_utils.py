import copy
import json
from typing import TYPE_CHECKING
from uuid import uuid4

import sentry_sdk
from core.database import mongodb
from motor_quote.enums import Insurer, TaskStatus
import requests
from requests import adapters
import httpx

if TYPE_CHECKING:
    from motor_quote.models import MotorQuoteRequest
    from motor_quote.serializers import MotorQuoteRequestCreateSerializer


class AevisUtils:

    URL = "https://aevis-auto.cruv.dev"
    GET_QUOTE_ENDPOINT = f"{URL}/automation/policy-request/get-quote"
    QUOTE_STATUS_ENDPOINT = f"{URL}/automation/policy-request/get-quote/status"
    QUOTE_RECORDING_ENDPOINT = f"{URL}/automation/policy-request/get-quote/recording"
    QUOTE_REQ_VALIDATION_ENDPOINT = f"{URL}/automation/policy-request/get-quote/validate"

    APP = "policyboss-8aojcu"
    API_KEY = "hiket9itretijuyoma6o9or2toplxemibre4ruzl"

    @staticmethod
    def create_quote_task(
        quote_request: "MotorQuoteRequest",
        request_serializer: "MotorQuoteRequestCreateSerializer",
    ):
        insurers: dict = request_serializer.data["insurers"]
        details: dict = request_serializer.data["details"]

        def post(session: requests.Session, app: str, insurer: dict, preassigned_credentials: dict = None):
            json = {"app": app, **insurer, **details}
            if preassigned_credentials:
                json["config"] = {"preassigned_credentials": preassigned_credentials}
            try:
                response = session.post(
                    __class__.GET_QUOTE_ENDPOINT,
                    json=json,
                    headers={"AUTHORIZATION": f"Bearer {__class__.API_KEY}"},
                )
                response.raise_for_status()
            except requests.RequestException as e:
                print(
                    f"Error creating quote task for insurer {insurer['insurer']}: {e}, {response.text}"
                )
                sentry_sdk.capture_exception(e)
                task_id = str(uuid4())
                mongodb._insert_one(
                    mongodb.quote_tasks,
                    {
                        "id": task_id,
                        "request_id": quote_request.mongo_id,
                        "insurer": insurer["insurer"],
                        "status": TaskStatus.FAILED.value,
                    },
                )
            else:
                result = response.json()
                task_id: str = result["request_id"]
                mongodb._insert_one(
                    mongodb.quote_tasks,
                    {
                        "id": task_id,
                        "request_id": quote_request.mongo_id,
                        "insurer": insurer["insurer"],
                        "status": TaskStatus.PENDING.value,
                        "data": json,
                    },
                )
                print(f"Created quote task {task_id} for insurer {insurer['insurer']}")

            return task_id

        task_ids = []
        with requests.Session() as session:
            session.mount(__class__.URL, adapters.HTTPAdapter(max_retries=3))
            for insurer in insurers:
                preassigned_credentials = None
                if quote_request.company.dns_config.sub_domain == "ideal":
                    if insurer["insurer"] == Insurer.RGCL.value:
                        preassigned_credentials =  {
                            "username": "15BRG210JYOTI",
                            "password": "Pass@123"
                        }
                    elif insurer["insurer"] == Insurer.ROYAL.value:
                        # TODO: Add Royal Sundaram preassigned credentials
                        pass
                task_ids.append(post(session, __class__.APP, insurer, preassigned_credentials))

        return task_ids

    @staticmethod
    def get_status(task_id: str):
        """Get the status of a quote request task."""
        with requests.Session() as session:
            session.mount(__class__.URL, adapters.HTTPAdapter(max_retries=3))
            try:
                response = session.get(
                    f"{__class__.QUOTE_STATUS_ENDPOINT}?request_id={task_id}",
                    headers={"AUTHORIZATION": f"Bearer {__class__.API_KEY}"},
                )
                response.raise_for_status()
                return True, response.json()
            except requests.RequestException as e:
                print(f"Error fetching status for task {task_id}: {e}")
                sentry_sdk.capture_exception(e)
                return False, None
            
    @staticmethod
    def get_recording(task_id: str):
        """Get the recording of a quote request task."""
        with requests.Session() as session:
            session.mount(__class__.URL, adapters.HTTPAdapter(max_retries=3))
            try:
                response = session.get(
                    f"{__class__.QUOTE_RECORDING_ENDPOINT}?request_id={task_id}",
                    headers={"AUTHORIZATION": f"Bearer {__class__.API_KEY}"},
                )
                response.raise_for_status()
                return True, response.json()
            except requests.RequestException as e:
                print(f"Error fetching status for task {task_id}: {e}")
                sentry_sdk.capture_exception(e)
                return False, None
            
    @staticmethod
    async def validate_quote_request(request_serializer: "MotorQuoteRequestCreateSerializer"):
        data = copy.deepcopy(request_serializer.data)
        data["details"]["app"] = __class__.APP
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    __class__.QUOTE_REQ_VALIDATION_ENDPOINT,
                    json=data,
                    headers={"AUTHORIZATION": f"Bearer {__class__.API_KEY}"},
                )
                if response.status_code == 422:
                    try:
                        response.raise_for_status()
                    except Exception as e:
                        print(f"Error validating quote request: {e}, {response.text}")
                        sentry_sdk.capture_exception(e)

                    return True, {"is_valid": False, "insurers": [], "error": response.text}
                
                response.raise_for_status()
                return True, response.json()
            except httpx.HTTPError as e:
                print(f"Error validating quote request: {e}")
                sentry_sdk.capture_exception(e)
                return False, None

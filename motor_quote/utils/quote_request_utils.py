from .aevis_utils import AevisUtils
from typing import TYPE_CHECKING
from core.database import mongodb


class QuoteRequestUtils:
    @staticmethod
    def update_task_status(task_id: str):
        success, status = AevisUtils.get_status(task_id)
        if success:
            # Update the task status in the database
            mongodb._update_one(
                mongodb.quote_tasks,
                {"id": task_id},
                {
                    "$set": {
                        "quote_status": status["policy_status"],
                        "status": status["policy_status"]["status"],
                    }
                },
            )

    @staticmethod
    def get_basic_details_projection():
        return {
            "details.product": 1,
            "details.product_type": 1,
            "details.product_sub_type": 1,
            "details.product_category": 1,
            "details.policy_category": 1,
            "details.policy_type": 1,
            "details.make": 1,
            "details.model": 1,
            "details.variant": 1,
            "details.transmission": 1,
            "details.policy_start_date": 1,
            "details.policy_expiry_date": 1,
            "details.business_type": 1,
            "details.registration_number_1": 1,
            "details.registration_number_2": 1,
            "details.registration_number_3": 1,
            "details.registration_number_4": 1,
            "details.make_month": 1,
            "details.make_year": 1,
            "details.vehicle_fuel_type": 1,
            "details.vehicle_engine_number": 1,
            "details.vehicle_chassis_number": 1,
        }
    
    @staticmethod
    def get_recording(task_id: str):
        success, recording_info = AevisUtils.get_recording(task_id)
        if success:
            return recording_info
        return None

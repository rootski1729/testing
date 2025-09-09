import httpx
import logging
import asyncio
from typing import Optional

from models import (
    StartCompanyProcessingRequest,
    PendingFileResponse,
    UpdateFileStatusRequest,
    PolicyExtractionRequest,
    PolicyExtractionResponse,
    PolicyExtractionObject,
    NovoupExtractionResponse,
    Insurer,
    Product,
    ProductType,
    ProductSubType,
    PolicyType,
    InsuredType
)
from locks import get_company_lock
from utils import (
    break_vehicle_number,
    clean_amount,
    clean_email,
    clean_ncb,
    clean_phone,
    clean_vehicle_gvw,
    vehicle_number_to_rta,
    vehicle_number_to_state,
    clean_insurer
)

logger = logging.getLogger(__name__)

# ====================== PROVIDER MAPPING ======================

PROVIDER_MAP = {
    "68678b51df5a5abb9e504573": {
        "insurer": Insurer.CHOLA,
        "product": Product.MOTOR,
        "product_type": ProductType.COMMERCIAL,
        "product_sub_type": None,
        "policy_type": PolicyType.TP,
    },
    "68678aab8d822bc79808357e": {
        "insurer": Insurer.MAGMA,
        "product": Product.MOTOR,
        "product_type": ProductType.COMMERCIAL,
        "product_sub_type": ProductSubType.GCV,
        "policy_type": PolicyType.PACKAGE,
    },
    "68678af2df5a5abb9e504569": {
        "insurer": Insurer.SHRIRAM,
        "product": Product.MOTOR,
        "product_type": ProductType.COMMERCIAL,
        "product_sub_type": None,
        "policy_type": None,
    },
    "68676ee08d822bc79808354b": {
        "insurer": Insurer.TATA,
        "product": Product.MOTOR,
        "product_type": None,
        "product_sub_type": None,
        "policy_type": None,
    },
    "68678ac18d822bc798083584": {
        "insurer": Insurer.UIIC,
        "product": Product.MOTOR,
        "product_type": ProductType.COMMERCIAL,
        "product_sub_type": ProductSubType.GCV,
        "policy_type": PolicyType.PACKAGE,
    },
    "68678ae18d822bc79808358a": {
        "insurer": Insurer.BAJAJ,
        "product": Product.HEALTH,
        "product_type": None,
        "product_sub_type": None,
        "policy_type": None,
    },
    "68678a5d8d822bc798083570": {
        "insurer": Insurer.NIC,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.PC,
        "policy_type": PolicyType.TP,
    },
    "68678a7ddf5a5abb9e504561": {
        "insurer": Insurer.GO,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.TW,
        "policy_type": PolicyType.PACKAGE,
    },
    "68678a4bdf5a5abb9e50455b": {
        "insurer": Insurer.ICICI,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.PC,
        "policy_type": PolicyType.PACKAGE,
    },
    "68678a99df5a5abb9e504565": {
        "insurer": Insurer.SBI,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.PC,
        "policy_type": PolicyType.TP,
    },
    "68678b1adf5a5abb9e50456d": {
        "insurer": Insurer.USGI,
        "product": Product.MOTOR,
        "product_type": None,
        "product_sub_type": ProductSubType.MISC,
        "policy_type": None,
    },
    "68678b028d822bc798083592": {
        "insurer": Insurer.KTKM,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.PC,
        "policy_type": PolicyType.TP,
    },
}

# ====================== DJANGO API SERVICES ======================

async def get_next_pending_file(django_base_url: str, company_id: str, jwt_token: str = None) -> Optional[PendingFileResponse]:
    """Get next pending file from Django API"""
    headers = {"Content-Type": "application/json"}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{django_base_url}/motor-policy/policy/next-pending-file/",
            params={"company_id": company_id},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return PendingFileResponse(**data)
        elif response.status_code == 404:
            return None  # No more files
        else:
            response.raise_for_status()

async def update_file_status(django_base_url: str, update_data: UpdateFileStatusRequest, jwt_token: str = None):
    """Update file processing status in Django"""
    headers = {"Content-Type": "application/json"}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{django_base_url}/motor-policy/policy/update-file-status/",
            json=update_data.model_dump(mode='json'),
            headers=headers,
            timeout=60
        )
        response.raise_for_status()

# ====================== FILE HANDLING SERVICES ======================

async def download_file(file_url: str) -> tuple:
    """Download file from URL (typically S3)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(file_url)
        response.raise_for_status()
        return response.content, response.headers.get("content-type", "application/pdf")

# ====================== PROVIDER IMPLEMENTATIONS ======================

class AbstractPolicyExtractionProvider:
    """Abstract base class for policy extraction providers"""
    
    def __init__(self):
        pass

    def run(self, request: PolicyExtractionRequest) -> PolicyExtractionResponse:
        """Extract policy data from the provided request"""
        raise NotImplementedError

class Novoup(AbstractPolicyExtractionProvider):
    """Novoup policy extraction provider implementation"""
    
    URL = "https://coral-app-aqae8.ondigitalocean.app/api/providers/extract"

    def __init__(self):
        super().__init__()

    def run(self, request: PolicyExtractionRequest) -> PolicyExtractionResponse:
        """Extract policy data using Novoup API"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.URL,
                    files={"pdf": request.file},
                )
                response.raise_for_status()

            provider_id = response.json()["providerID"]
            extracted_data = response.json().get("extractedData", {})
            extract = NovoupExtractionResponse(**extracted_data)
            provider_info = PROVIDER_MAP.get(provider_id, {})

            obj = PolicyExtractionObject(
                insurer=provider_info.get("insurer"),
                product=provider_info.get("product"),
                product_type=(
                    ProductType.PRIVATE
                    if provider_info.get("product_sub_type")
                    in [ProductSubType.PC, ProductSubType.TW]
                    else ProductType.COMMERCIAL
                ),
                product_sub_type=provider_info.get("product_sub_type"),
                product_category=extract.product_category,
                policy_category=extract.calc_policy_category(provider_info),
                policy_type=extract.calc_policy_type(provider_info),
                vehicle_registration_state=vehicle_number_to_state(extract.vehicle_number),
                make=extract.make,
                model=extract.model,
                registration_number_1=break_vehicle_number(extract.vehicle_number)[0] if break_vehicle_number(extract.vehicle_number) else None,
                registration_number_2=break_vehicle_number(extract.vehicle_number)[1] if break_vehicle_number(extract.vehicle_number) else None,
                registration_number_3=break_vehicle_number(extract.vehicle_number)[2] if break_vehicle_number(extract.vehicle_number) else None,
                registration_number_4=break_vehicle_number(extract.vehicle_number)[3] if break_vehicle_number(extract.vehicle_number) else None,
                vehicle_registration_date=extract.registration_date,
                make_year=extract.manufacturing_year,
                vehicle_fuel_type=extract.vehicle_fuel_type,
                vehicle_engine_number=extract.engine_number,
                vehicle_chassis_number=extract.chassis_number,
                vehicle_seating_capacity=extract.seating_capacity,
                vehicle_cc=extract.engine_capacity_cc,
                insured_type=(
                    InsuredType.INDIVIDUAL
                    if extract.business_type
                    and extract.business_type.lower() == "individual"
                    else None
                ),
                insured_name=extract.customer_name,
                insured_address=extract.customer_address,
                insured_mobile=clean_phone(extract.customer_phone),
                insured_email=clean_email(extract.customer_email),
                vehicle_rta=vehicle_number_to_rta(extract.vehicle_number, extract.rto_code),
                vehicle_idv=clean_amount(extract.vehicle_idv),
                last_policy_available=extract.last_policy_available,
                last_insurer=clean_insurer(extract.previous_insurer_name),
                last_policy_number=extract.previous_policy_number,
                last_policy_to=extract.previous_policy_end_date or extract.prev_policy_expiry,
                last_policy_ncb_percent=clean_ncb(extract.previous_ncb),
                vehicle_gvw=clean_vehicle_gvw(extract.gross_vehicle_weight),
                # Policy details
                policy_number=extract.policy_number,
                issue_date=extract.issue_date,
                od_start_date=extract.od_start_date,
                od_end_date=extract.od_end_date,
                tp_start_date=extract.tp_start_date,
                tp_end_date=extract.tp_end_date,
                sum_insured=clean_amount(extract.sum_insured),
                basic_od_premium=clean_amount(extract.basic_od_premium),
                total_od_premium=clean_amount(extract.total_od_premium),
                total_od_add_on_premium=clean_amount(extract.total_od_add_on_premium),
                basic_tp_premium=clean_amount(extract.basic_tp_premium),
                total_tp_premium=clean_amount(extract.total_tp_premium),
                total_tp_add_on_premium=clean_amount(extract.total_tp_add_on_premium),
                net_premium=clean_amount(extract.net_premium),
                taxes=clean_amount(extract.taxes),
                taxes_rate=clean_ncb(extract.taxes_rate),
                gross_discount=clean_amount(extract.gross_discount),
                total_premium=clean_amount(extract.total_premium),
                ncb=clean_ncb(extract.ncb),
                broker_name=extract.broker_name,
                broker_email=clean_email(extract.broker_email),
                broker_code=extract.broker_code,
            )
            
            return PolicyExtractionResponse(
                is_success=True,
                message="Policy extracted successfully",
                response=obj
            )
            
        except Exception as e:
            logger.error(f"Novoup extraction failed: {str(e)}")
            return PolicyExtractionResponse(
                is_success=False,
                message=f"Policy extraction failed: {str(e)}",
                response=PolicyExtractionObject()
            )

# ====================== CORE PROCESSING SERVICES ======================

async def extract_policy_data(file_url: str) -> dict:
    """Extract policy data from file URL using the configured provider"""
    try:
        # Download file from URL
        file_bytes, content_type = await download_file(file_url)
        
        # Create extraction request
        payload = PolicyExtractionRequest(
            file=("policy.pdf", file_bytes, content_type)
        )
        
        # Use Novoup provider for extraction
        provider = Novoup()
        result = provider.run(payload)
        
        if result.is_success:
            return {
                "success": True,
                "data": result.response.model_dump(mode='json',by_alias= True)
            }
        else:
            return {
                "success": False,
                "error": result.message
            }
            
    except Exception as e:
        logger.error(f"Policy data extraction failed: {str(e)}")
        return {
            "success": False,
            "error": "Policy data extraction failed: Client error '404 Not Found' for given URL"
        }

async def process_company_files_with_acquired_lock(request_data: StartCompanyProcessingRequest, company_lock: asyncio.Lock):
    """
    Race-condition-free processing function with already-acquired lock.
    The lock is already acquired before this function is called.
    """
    try:
        logger.info(f"Starting pull-based processing for company {request_data.company_id}")
        processed_count = 0
        
        while True:
            # Get next pending file from Django API
            pending_file = await get_next_pending_file(
                request_data.django_base_url, 
                request_data.company_id, 
                request_data.jwt_token
            )
            
            if not pending_file:
                logger.info(f"No more pending files for company {request_data.company_id}")
                break
            
            logger.info(f"Processing file: {pending_file.mongo_id}")
            
            # Extract policy data from the file
            result = await extract_policy_data(pending_file.file_url)
            
            # Prepare update data for Django API
            update_data = UpdateFileStatusRequest(
                mongo_id=pending_file.mongo_id,
                success=result["success"],
                extracted_data=result.get("data") if result["success"] else None,
                error=result.get("error") if not result["success"] else None
            )
            
            # Update file status in Django
            try:
                await update_file_status(
                    request_data.django_base_url, 
                    update_data, 
                    request_data.jwt_token
                )
                processed_count += 1
                logger.info(f"Successfully processed: {pending_file.mongo_id}")
            except Exception as e:
                logger.error(f"Failed to update status for {pending_file.mongo_id}: {str(e)}")
        
        logger.info(f"Completed processing for company {request_data.company_id}, processed {processed_count} files")
        
    except Exception as e:
        logger.error(f"Fatal error in processing company {request_data.company_id}: {str(e)}")
    finally:
        # Always release the lock when done (success or failure)
        if company_lock.locked():
            company_lock.release()
            logger.info(f"Released lock for company {request_data.company_id}")

async def process_company_files(request_data: StartCompanyProcessingRequest):
    """
    Legacy processing function - pulls files from Django API and processes them.
    Uses company-specific locks to prevent concurrent processing.
    (This is kept for backward compatibility)
    """
    company_lock = await get_company_lock(request_data.company_id)
    
    async with company_lock:
        logger.info(f"Starting pull-based processing for company {request_data.company_id}")
        processed_count = 0
        
        while True:
            # Get next pending file from Django API
            pending_file = await get_next_pending_file(
                request_data.django_base_url, 
                request_data.company_id, 
                request_data.jwt_token
            )
            
            if not pending_file:
                logger.info(f"No more pending files for company {request_data.company_id}")
                break
            
            logger.info(f"Processing file: {pending_file.mongo_id}")
            
            # Extract policy data from the file
            result = await extract_policy_data(pending_file.file_url)
            
            # Prepare update data for Django API
            update_data = UpdateFileStatusRequest(
                mongo_id=pending_file.mongo_id,
                success=result["success"],
                extracted_data=result.get("data") if result["success"] else None,
                error=result.get("error") if not result["success"] else None
            )
            
            # Update file status in Django
            try:
                await update_file_status(
                    request_data.django_base_url, 
                    update_data, 
                    request_data.jwt_token
                )
                processed_count += 1
                logger.info(f"Successfully processed: {pending_file.mongo_id}")
            except Exception as e:
                logger.error(f"Failed to update status for {pending_file.mongo_id}: {str(e)}")
        
        logger.info(f"Completed processing for company {request_data.company_id}, processed {processed_count} files")

# ====================== HEALTH CHECK SERVICE ======================

def health_check():
    """Simple health check service"""
    return {"status": "healthy", "service": "policy-extraction"}
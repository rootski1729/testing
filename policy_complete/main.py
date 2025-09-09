from fastapi import FastAPI, BackgroundTasks
import logging
import asyncio

from models import StartCompanyProcessingRequest
from services import process_company_files_with_acquired_lock  # Fixed import
from locks import get_company_lock, try_acquire_company_lock_immediately, check_company_processing_status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Policy Extraction Microservice", version="1.0.0")

# ====================== API ENDPOINTS ======================

@app.post("/start-company-processing")
async def start_company_processing(request: StartCompanyProcessingRequest, background_tasks: BackgroundTasks):
    """Start pull-based processing for a company (race-condition-free)"""
    
    # Atomically try to acquire company lock immediately
    acquired, company_lock = await try_acquire_company_lock_immediately(request.company_id)  # Fixed function name
    
    if not acquired:
        return {
            "status": "already_processing",
            "message": f"Company {request.company_id} is already being processed"
        }
    
    # Lock acquired - start background processing with the acquired lock
    background_tasks.add_task(process_company_files_with_acquired_lock, request, company_lock)  # Fixed function call
    
    return {
        "status": "started",
        "company_id": request.company_id,
        "message": "Pull-based processing started"
    }

@app.get("/status/{company_id}")
async def get_company_status(company_id: str):
    """Check if company is currently being processed"""
    is_processing = await check_company_processing_status(company_id)  # Fixed to use correct function
    return {
        "company_id": company_id,
        "is_processing": is_processing
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "policy-extraction"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
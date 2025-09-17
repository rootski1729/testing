import asyncio
import threading

# Company-specific locks to prevent concurrent processing
COMPANY_LOCKS = {}

# Thread-safe lock for creating company locks
_LOCK_CREATION_LOCK = threading.Lock()

async def get_company_lock(company_id: str) -> asyncio.Lock:
    """
    Thread-safe function to get or create a lock for the specified company.
    
    Args:
        company_id (str): The unique identifier for the company
        
    Returns:
        asyncio.Lock: The lock object for the company
    """
    # Use synchronous lock to prevent race conditions during lock creation
    with _LOCK_CREATION_LOCK:
        if company_id not in COMPANY_LOCKS:
            COMPANY_LOCKS[company_id] = asyncio.Lock()
    return COMPANY_LOCKS[company_id]

async def try_acquire_company_lock_immediately(company_id: str) -> tuple[bool, asyncio.Lock]:
    """
    Atomically try to acquire company lock immediately to prevent race conditions.
    
    Args:
        company_id (str): The unique identifier for the company
        
    Returns:
        tuple[bool, asyncio.Lock]: (acquired, lock) where acquired indicates if lock was successfully acquired
    """
    company_lock = await get_company_lock(company_id)
    
    # Check if lock is already held
    if company_lock.locked():
        return False, company_lock
    
    # Try to acquire the lock with a very short timeout
    try:
        await asyncio.wait_for(company_lock.acquire(), timeout=0.001)
        return True, company_lock
    except asyncio.TimeoutError:
        # Lock was acquired by someone else in the tiny window
        return False, company_lock

async def check_company_processing_status(company_id: str) -> bool:
    """
    Check if company is currently being processed.
    
    Args:
        company_id (str): The unique identifier for the company
        
    Returns:
        bool: True if company is currently being processed
    """
    company_lock = await get_company_lock(company_id)
    return company_lock.locked()
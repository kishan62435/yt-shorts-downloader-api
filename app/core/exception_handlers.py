import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


# Function to get a cleaned traceback with a limited number of lines
def get_clean_traceback(exc_info, limit=2):
    # Format the traceback and split it into lines
    exc_lines = traceback.format_exception(*exc_info)
    # Limit the number of lines to the last 'limit' lines
    # return "\n".join(exc_lines[-limit:])
    return "".join(exc_lines[-limit:])



# Custom Exception Handler for Validation Errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # logger.exception(f"Validation error occurred: {exc}")
    exc_info = (type(exc), exc, exc.__traceback__)
    clean_traceback = get_clean_traceback(exc_info)
    
    # Log the error
    logger.error(f"Validation error occurred: {exc} - Traceback: {clean_traceback}")
    return JSONResponse(
        status_code=422,  # or 400 depending on your needs
        content={"message": "Validation Error", "details": exc.errors()},
    )

# Default Exception Handler for unhandled exceptions
async def general_exception_handler(request: Request, exc: Exception):
    # logger.exception(f"Unhandled exception occurred: {exc}")
    exc_info = (type(exc), exc, exc.__traceback__)
    clean_traceback = get_clean_traceback(exc_info)
    
    # Log the error
    logger.error(f"Unhandled exception occurred: {exc} - Traceback: {clean_traceback}")

    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    # logger.exception(f"HTTP error occurred: {exc.detail}")
    exc_info = (type(exc), exc, exc.__traceback__)
    clean_traceback = get_clean_traceback(exc_info)
    
    # Log the error
    logger.error(f"HTTP error occurred: {exc.detail} - Traceback: {clean_traceback}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": "HTTP error occurred", "details": exc.detail},
    )

from fastapi import Request
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

class AppException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code

async def app_exception_handler(request: Request, exc: AppException):
    logger.warning("app_error", path=str(request.url), message=exc.message, code=exc.code)
    return JSONResponse(status_code=exc.code, content={"error": exc.message})

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", path=str(request.url), error=str(exc), exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})

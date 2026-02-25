from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.core.exceptions import SalesPulseException
from src.core.logging import logger


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SalesPulseException)
    async def salespulse_exception_handler(request: Request, exc: SalesPulseException):
        logger.error(f"SalesPulseException: {exc.message} | path={request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"},
        )

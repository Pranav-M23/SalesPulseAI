import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from src.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        method = request.method
        path = request.url.path

        # Skip logging for docs/static
        if path in ("/docs", "/redoc", "/openapi.json", "/favicon.ico"):
            return await call_next(request)

        logger.info(f"--> {method} {path}")
        try:
            response = await call_next(request)
        except Exception as e:
            duration = round((time.perf_counter() - start) * 1000, 2)
            logger.error(f"<-- {method} {path} | 500 | {duration}ms | {e}")
            raise
        duration = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"<-- {method} {path} | {response.status_code} | {duration}ms")
        return response

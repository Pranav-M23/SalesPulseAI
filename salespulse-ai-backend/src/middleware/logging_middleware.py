from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time

        logging.info(
            f"Request: {request.method} {request.url} - "
            f"Response status: {response.status_code} - "
            f"Processing time: {process_time:.2f} seconds"
        )
        return response
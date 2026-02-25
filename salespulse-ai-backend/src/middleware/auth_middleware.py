from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from your_project_name.core.security import verify_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if not token or not verify_token(token):
            raise HTTPException(status_code=403, detail="Not authorized")
        response = await call_next(request)
        return response

def add_auth_middleware(app):
    app.add_middleware(AuthMiddleware)
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.services.auth_service import AuthService

router = APIRouter()

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin, auth_service: AuthService = Depends()):
    token = await auth_service.authenticate(user.username, user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register(user: UserLogin, auth_service: AuthService = Depends()):
    token = await auth_service.register(user.username, user.password)
    if not token:
        raise HTTPException(status_code=400, detail="Registration failed")
    return {"access_token": token, "token_type": "bearer"}
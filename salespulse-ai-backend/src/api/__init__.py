# src/api/__init__.py

from fastapi import APIRouter

router = APIRouter()

from .v1.router import router as v1_router

router.include_router(v1_router, prefix="/v1", tags=["v1"])
from fastapi import APIRouter
from .v1.routes import async_routes_v1

router = APIRouter()

router.include_router(async_routes_v1.router, prefix="/v1/async", tags=["async"])
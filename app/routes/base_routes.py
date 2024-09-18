from fastapi import APIRouter
from .v1 import basic_routes_v1

router = APIRouter()

router.include_router(basic_routes_v1.router, prefix="/v1/basic", tags=["basic"])
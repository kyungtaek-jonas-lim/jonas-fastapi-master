from fastapi import APIRouter
from .v1.routes \
    import async_routes_v1, file_routes_v1, redis_routes_v1

router = APIRouter()

router.include_router(async_routes_v1.router, prefix="/v1/async", tags=["async"])
router.include_router(file_routes_v1.router, prefix="/v1/file", tags=["file"])
router.include_router(redis_routes_v1.router, prefix="/v1/redis", tags=["redis"])
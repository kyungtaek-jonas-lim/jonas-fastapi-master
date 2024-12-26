from fastapi import APIRouter
from .v1.routes \
    import async_routes_v1, file_routes_v1, redis_routes_v1, jwt_routes_v1, websocket_routes_v1

router_v1 = APIRouter()

router_v1.include_router(async_routes_v1.router, prefix="/async", tags=["async"])
router_v1.include_router(file_routes_v1.router, prefix="/file", tags=["file"])
router_v1.include_router(redis_routes_v1.router, prefix="/redis", tags=["redis"])
router_v1.include_router(jwt_routes_v1.router, prefix="/jwt", tags=["jwt"])
router_v1.include_router(websocket_routes_v1.router, prefix="/websocket", tags=["websocket"])
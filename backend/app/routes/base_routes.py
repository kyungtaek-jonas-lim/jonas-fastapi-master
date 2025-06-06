from fastapi import APIRouter
from .v1.routes \
    import async_routes_v1, cryptography_routes_v1, file_routes_v1, jwt_routes_v1, mongodb_routes_v1, redis_routes_v1, websocket_routes_v1, kafka_routes_v1

router_v1 = APIRouter()

router_v1.include_router(async_routes_v1.router, prefix="/async", tags=["async"])
router_v1.include_router(cryptography_routes_v1.router, prefix="/cryptography", tags=["cryptography"])
router_v1.include_router(file_routes_v1.router, prefix="/file", tags=["file"])
router_v1.include_router(jwt_routes_v1.router, prefix="/jwt", tags=["jwt"])
router_v1.include_router(mongodb_routes_v1.router, prefix="/mongodb", tags=["mongodb"])
router_v1.include_router(redis_routes_v1.router, prefix="/redis", tags=["redis"])
router_v1.include_router(websocket_routes_v1.router, prefix="/websocket", tags=["websocket"])
router_v1.include_router(kafka_routes_v1.router, prefix="/kafka", tags=["kafka"])
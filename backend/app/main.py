from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.base_routes import router_v1
from app.config import current_config
from app.scheduler import start_scheduler_async_io, start_scheduler_background, shutdown_scheduler
from app.kafka.config import KafkaConfig
from app.kafka.producer import get_kafka_producer
from app.kafka.consumer import consume
import asyncio

app = FastAPI()

# =========================================================
# Add middleware
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=current_config.ORIGIN.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Include routers
# =========================================================

app.include_router(router_v1, prefix="/v1")


# =========================================================
# Basic Routes
# =========================================================

# Health Check
@app.get("/health_check")
def read_root():
    response = {
        "status": 200,
        "message": "healthy"
    }
    return response


# =========================================================
# App Event
# =========================================================

@app.on_event("startup")
async def startup_event():
    if current_config.SCHEDULER:
        print("Schedulers are activated")
        start_scheduler_async_io()
        start_scheduler_background()
    else:
        print("Schedulers are deactivated")
    
    # Create Kafka Consumer
    if KafkaConfig.ON.value:
        await get_kafka_producer()
        asyncio.create_task(consume())

@app.on_event("shutdown")
async def shutdown_event():
    if current_config.SCHEDULER:
        shutdown_scheduler()
        print("Shutdown schedulers")
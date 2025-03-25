from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.kafka.producer import send_to_kafka
from app.kafka.config import KafkaConfig

router = APIRouter()

# =========================================================
# API Request
# =========================================================
class CreateItemRequest(BaseModel):
    id: int
    name: str
    description: str = None

@router.post("/create_item")
async def create_item(request: CreateItemRequest):
    await send_to_kafka(KafkaConfig.TOPIC.value, request.dict())
    return {"message": "Item sent to Kafka"}
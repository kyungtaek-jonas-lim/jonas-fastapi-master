import os
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

router = APIRouter()

# =========================================================
# MongoDB Settings
# =========================================================

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URI)
db = client["jonas-fastapi-master"]  # Replace with your DB name
collection = db["items"]  # Replace with your collection name


# =========================================================
# Pydantic Models
# =========================================================

class ItemModel(BaseModel):
    name: str = Field(...)
    description: Optional[str] = Field(None)
    price: float = Field(...)

class ItemResponse(ItemModel):
    id: str = Field(...)


# =========================================================
# Helper
# =========================================================

def serialize_item(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item.get("description"),
        "price": item["price"]
    }


# =========================================================
# MongoDB CRUD Routes
# =========================================================

@router.post("/create", response_model=ItemResponse)
async def create_item(item: ItemModel):
    result = await collection.insert_one(item.dict())
    created = await collection.find_one({"_id": result.inserted_id})
    return serialize_item(created)


@router.get("/get/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str = Path(...)):
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return serialize_item(item)


@router.put("/update/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item: ItemModel):
    result = await collection.update_one({"_id": ObjectId(item_id)}, {"$set": item.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = await collection.find_one({"_id": ObjectId(item_id)})
    return serialize_item(updated)


@router.delete("/delete/{item_id}", response_model=dict)
async def delete_item(item_id: str):
    result = await collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "id": item_id}
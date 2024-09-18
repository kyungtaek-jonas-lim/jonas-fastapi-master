from fastapi import APIRouter

router = APIRouter()

@router.get("")
def basic():
    return {"message": "succeeded in uploading!"}
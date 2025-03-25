import os
import redis
from enum import Enum
from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()


# =========================================================
# Settings
# =========================================================

redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'host.docker.internal'), # replace to the host of Redis service
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB_INDEX', 0)), # db index (up to 15)
    decode_responses=True if os.getenv('REDIS_DECODE_RESPONSES', 'True') == 'True' else False # True: string to UTF-8 (str type in python)
)

LOCK_TIMEOUT = 5

# Redis Value Type
class RedisValueType(Enum):
    STRING      = ("STRING",    "string:",      "lock_string_")
    SET         = ("SET",       "set:",         "lock_set_")
    HASH        = ("HASH",      "hash:",        "lock_hash")

    def __new__(cls, key, key_prefix, lock_prefix):
        obj = object.__new__(cls)
        obj._value_ = key  # Use _value_ for the key
        obj.key = key
        obj.key_prefix = key_prefix
        obj.lock_prefix = lock_prefix
        return obj


# =========================================================
# API Request
# =========================================================

class RedisRequest(BaseModel):
    ttl: Optional[int] = Field(None)

class RedisStringRequest(RedisRequest):
    value: str = Field(...)

class RedisSetRequest(RedisRequest):
    members: list = Field(...)

class RedisHashRequest(RedisRequest):
    fields: dict = Field(...)


# =========================================================
# API Response
# =========================================================

class RedisResponse(BaseModel):
    status: Optional[str] = Field(None)
    key: str = Field(...)

class RedisStringResponse(RedisResponse):
    value: Optional[str] = Field(None)

class RedisSetResponse(RedisResponse):
    members: Optional[list] = Field(None)

class RedisHashResponse(RedisResponse):
    fields: Optional[dict] = Field(None)


# =========================================================
# Redis String API
# =========================================================

@router.get("/string/{key}", response_model=RedisStringResponse)
async def get_string(key: str = Path(..., min_length=1)):
    actual_key = RedisValueType.STRING.key_prefix + key
    value = redis_client.get(actual_key)
    if value is not None:
        return RedisStringResponse (
            status="success",
            key= key,
            value= value
        )
    raise HTTPException(status_code=404, detail="Key not found")


@router.post("/string/{key}", response_model=RedisStringResponse)
async def add_string(
    request: RedisStringRequest,
    key: str = Path(..., min_length=1)
):
    actual_key = RedisValueType.STRING.key_prefix + key
    if redis_client.exists(actual_key):
        raise HTTPException(status_code=400, detail="Key already exists")
    
    lock_key = RedisValueType.STRING.lock_prefix + key
    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            redis_client.set(actual_key, request.value)

            if request.ttl:
                redis_client.expire(actual_key, request.ttl)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")

    return RedisStringResponse(
        status="success",
        key= key,
        value= request.value
    )


@router.put("/string/{key}", response_model=RedisStringResponse)
async def update_string(
    request: RedisStringRequest,
    key: str = Path(..., min_length=1)
):
    actual_key = RedisValueType.STRING.key_prefix + key
    if not redis_client.exists(actual_key):
        raise HTTPException(status_code=404, detail="Key not found")
    
    lock_key = RedisValueType.STRING.lock_prefix + key
    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            redis_client.set(actual_key, request.value)
            if request.ttl:
                redis_client.expire(actual_key, request.ttl)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")
    
    return RedisStringResponse(
        status="success",
        key= key,
        value= request.value
    )


@router.delete("/string/{key}", response_model=RedisStringResponse)
async def delete_string(key: str = Path(..., min_length=1)):
    actual_key = RedisValueType.STRING.key_prefix + key
    
    lock_key = RedisValueType.STRING.lock_prefix + key

    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            result = redis_client.delete(actual_key)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")
    
    if result > 0:
        return RedisStringResponse(
            status="success",
            key=key
        )
    raise HTTPException(status_code=404, detail="Key not found")


# =========================================================
# Redis Set API
# =========================================================

@router.get("/set/{key}", response_model=RedisSetResponse)
async def get_set(key: str = Path(..., min_length=1)):
    actual_key = RedisValueType.SET.key_prefix + key
    members = redis_client.smembers(actual_key)
    if members:
        return RedisSetResponse(
            status="success",
            key=key,
            members=list(members)
        )
    raise HTTPException(status_code=404, detail="Key not found")


@router.post("/set/{key}", response_model=RedisSetResponse)
async def add_set(
    request: RedisSetRequest,
    key: str = Path(..., min_length=1)
):
    actual_key = RedisValueType.SET.key_prefix + key
    if redis_client.exists(actual_key):
        raise HTTPException(status_code=400, detail="Key already exists")

    lock_key = RedisValueType.SET.lock_prefix + key
    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            for member in request.members:
                redis_client.sadd(actual_key, member)

            if request.ttl:
                redis_client.expire(actual_key, request.ttl)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")

    return RedisSetResponse(
        status="success",
        key=key,
        members=list(request.members)
    )


@router.put("/set/{key}", response_model=RedisSetResponse)
async def update_set(
    request: RedisSetRequest,
    key: str = Path(..., min_length=1)
):
    actual_key = RedisValueType.SET.key_prefix + key
    if not redis_client.exists(actual_key):
        raise HTTPException(status_code=404, detail="Key not found")
    
    lock_key = RedisValueType.SET.lock_prefix + key
    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            redis_client.delete(actual_key)
            redis_client.sadd(actual_key, *request.members)

            if request.ttl:
                redis_client.expire(actual_key, request.ttl)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")

    return RedisSetResponse(
        status="success",
        key=key,
        members=list(request.members)
    )


@router.delete("/set/{key}", response_model=RedisSetResponse)
async def delete_set(key: str = Path(..., min_length=1)):
    actual_key = RedisValueType.SET.key_prefix + key
    
    lock_key = RedisValueType.SET.lock_prefix + key
    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            result = redis_client.delete(actual_key)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")
    
    if result > 0:
        return RedisSetResponse(
            status="success",
            key=key
        )
    raise HTTPException(status_code=404, detail="Key not found")



# =========================================================
# Redis Hash API
# =========================================================

@router.get("/hash/{key}", response_model=RedisHashResponse)
async def get_hash(key: str = Path(..., min_length=1)):
    actual_key = RedisValueType.HASH.key_prefix + key
    fields = redis_client.hgetall(actual_key)
    if fields:
        return RedisHashResponse(
            status="success",
            key=key,
            fields=fields
        )
    raise HTTPException(status_code=404, detail="Key not found")


@router.post("/hash/{key}", response_model=RedisHashResponse)
async def add_hash(
    request: RedisHashRequest,
    key: str = Path(..., min_length=1)
):
    actual_key = RedisValueType.HASH.key_prefix + key
    if redis_client.exists(actual_key):
        raise HTTPException(status_code=400, detail="Key already exists")
    
    lock_key = RedisValueType.HASH.lock_prefix + key
    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            redis_client.hmset(actual_key,request.fields)
            
            if request.ttl:
                redis_client.expire(actual_key, request.ttl)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")

    return RedisHashResponse(
        status="success",
        key= key,
        fields=request.fields
    )


@router.put("/hash/{key}", response_model=RedisHashResponse)
async def update_hash(
    request: RedisHashRequest,
    key: str = Path(..., min_length=1)
):
    actual_key = RedisValueType.HASH.key_prefix + key
    if not redis_client.exists(actual_key):
        raise HTTPException(status_code=404, detail="Key not found")
    
    lock_key = RedisValueType.HASH.lock_prefix + key
    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            redis_client.delete(actual_key)
            redis_client.hmset(actual_key, request.fields)

            if request.ttl:
                redis_client.expire(actual_key, request.ttl)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")

    return RedisHashResponse(
        status="success",
        key= key,
        fields=request.fields
    )
    

@router.delete("/hash/{key}", response_model=RedisHashResponse)
async def delete_hash(key: str = Path(..., min_length=1)):
    actual_key = RedisValueType.HASH.key_prefix + key
    
    lock_key = RedisValueType.HASH.lock_prefix + key
    lock = redis_client.lock(lock_key, timeout=LOCK_TIMEOUT)
    if lock.acquire(blocking=True): # blocking=True means it will wait for the turn (But unlike Reddison in Java, it doesn't use queuing system, just all the process competes to acquire the lock)
        try:
            result = redis_client.delete(actual_key)
        finally:
            lock.release()
    else:
        raise HTTPException(status_code=429, detail="Could not acquire lock, try again later")
    
    if result > 0:
        return RedisHashResponse(
            status="success",
            key=key
        )
    raise HTTPException(status_code=404, detail="Key not found")
from enum import Enum
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional
from jose import jwt
import datetime

router = APIRouter()


# =========================================================
# Settings
# =========================================================

# JWT Algorithm Type
class JwtAlgorithmType(Enum):
    HS256 = "HS256"
    RS256 = "RS256"

# Read the private key and public key from files
with open('keys/private.pem') as f:
    PRIVATE_KEY = f.read()

with open('keys/public.pem') as f:
    PUBLIC_KEY = f.read()
    

# =========================================================
# API Request
# =========================================================
class GenerateTokenRequest(BaseModel):
    user_id: str = Field(default=None)

class VerifyTokenRequest(BaseModel):
    token: str = Field(default=None)


# =========================================================
# Generate JWT (RS256)
# =========================================================
@router.post("/generate-token")
def generate_token(request:GenerateTokenRequest):
    payload = {
        "user_id": request.user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30) # Expires in 30 mins
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm=JwtAlgorithmType.RS256.value)
    return {"token": token}


# =========================================================
# Verify JWT (RS256)
# =========================================================
@router.post("/verify-token")
def verify_token(request:VerifyTokenRequest):
    return verify_token_logic(request.token)

def verify_token_logic(token: str):
    try:
        decoded_payload = jwt.decode(token, PUBLIC_KEY, algorithms=[JwtAlgorithmType.RS256.value])
        return {"decoded_payload": decoded_payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status=401, detail="Signature has expired.")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error.")


# =========================================================
# Protected route that requires JWT in Authorization header
# =========================================================
@router.get("/protected")
def protected_route(authorization: str = Header(...)):
    # Extract the token from the Authorization header
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header.")
    
    token = authorization.split(" ")[1] # Get the token part after "Bearer"

    decoded_payload = verify_token_logic(token)
    return {"user_id": decoded_payload["decoded_payload"]["user_id"]}
from enum import Enum
from typing import Tuple
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
    
# JWT Params
class JwtParams(Enum):
    USER_ID = "user_id"
    EXP = "exp"

# JWT Response Params
class JwtApiResponseParams(Enum):
    TOKEN = "token"
    DECODED_PAYLOAD = "decoded_payload"
    STATUS = "status"
    DETAIL = "detail"

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
    id = request.user_id
    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=30) # Expires in 30 mins
    return {JwtApiResponseParams.TOKEN.value: generate_token_logic(id=id, exp=exp)}

def generate_token_logic(id: str, exp: datetime) -> str:
    if not id or not id.strip() or not exp:
        raise HTTPException(status_code=400, detail="Bad Request.")
    payload = {
        JwtParams.USER_ID.value: id,
        JwtParams.EXP.value: exp
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=JwtAlgorithmType.RS256.value)
    


# =========================================================
# Verify JWT (RS256)
# =========================================================
@router.post("/verify-token")
def verify_token(request:VerifyTokenRequest):
    return verify_token_logic(request.token)

def verify_token_logic(token: str):
    try:
        decoded_payload = jwt.decode(token, PUBLIC_KEY, algorithms=[JwtAlgorithmType.RS256.value])
        return {JwtApiResponseParams.DECODED_PAYLOAD.value: decoded_payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status=401, detail="Signature has expired.")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error.")

def verify_token_logic_for_websocket(token: str) -> Tuple[bool, dict]:
    try:
        decoded_payload = jwt.decode(token, PUBLIC_KEY, algorithms=[JwtAlgorithmType.RS256.value])
        return True, decoded_payload
    except jwt.ExpiredSignatureError:
        return False, {JwtApiResponseParams.STATUS.value: 401, JwtApiResponseParams.DETAIL.value: "Signature has expired."}
    except jwt.JWTError:
        return False, {JwtApiResponseParams.STATUS.value: 401, JwtApiResponseParams.DETAIL.value: "Invalid token."}
    except Exception:
        return False, {JwtApiResponseParams.STATUS.value: 500, JwtApiResponseParams.DETAIL.value: "Internal Server Error."}


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
from enum import Enum
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from datetime import datetime, timedelta
from .jwt_routes_v1 import JwtParams, JwtApiResponseParams, verify_token_logic_for_websocket

router = APIRouter()
log_prefix = "[WEBSOCKET]"


# =========================================================
# Settings
# =========================================================

# WebSocket Close Codes
class WebsocketCloseCode(Enum):
    CLOSE_NORMAL = 1000  # Normal Closure: The connection successfully closed.
    CLOSE_GOING_AWAY = 1001  # Going Away: The server or client is going away (e.g., server shutting down).
    CLOSE_PROTOCOL_ERROR = 1002  # Protocol Error: The connection was closed due to a protocol error.
    CLOSE_UNSUPPORTED_DATA = 1003  # Unsupported Data: The connection was closed because the server does not support the data type.
    CLOSE_NO_STATUS_RECEIVED = 1005  # No Status Received: The connection was closed without receiving a close status.
    CLOSE_ABNORMAL_CLOSURE = 1006  # Abnormal Closure: The connection was closed abnormally (e.g., network failure).
    CLOSE_INVALID_PAYLOAD_DATA = 1007  # Invalid Payload Data: The connection was closed due to invalid payload data.
    CLOSE_POLICY_VIOLATION = 1008  # Policy Violation: The connection was closed due to policy violation.
    CLOSE_MESSAGE_TOO_BIG = 1009  # Message Too Big: The connection was closed because the message was too large.
    CLOSE_MANDATORY_EXTENSION = 1010  # Mandatory Extension: The connection was closed because the server requires a mandatory extension.
    CLOSE_INTERNAL_SERVER_ERROR = 1011  # Internal Server Error: The connection was closed due to an internal server error.
    CLOSE_TLS_HANDSHAKE_FAILURE = 1015  # TLS Handshake Failure: The connection was closed due to a failure in the TLS handshake.


# =========================================================
# Websocket Connection Manager
# =========================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, datetime] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = datetime.utcnow()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    def update_last_ping(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections[websocket] = datetime.utcnow()

    async def broadcast(self, message: str):
        for websocket in self.active_connections:
            await websocket.send_text(message)
    
    async def send_message(self, websocket: WebSocket, message: str):
        if websocket in self.active_connections:
            await websocket.send_text(message)

connection_manager = ConnectionManager()


# =========================================================
# Websocket Connect
# =========================================================
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    '''
    @params
        - token: JWT Token from '/jwt/generate_token' API for authorization
    '''

    # Authorization
    verified: bool
    verification_result: dict
    verified, verification_result = verify_token_logic_for_websocket(token)
    if not verified:
        print(f"{log_prefix} Websocket connection error! - {verification_result.get(JwtApiResponseParams.DETAIL.value, '')}")
        await websocket.close(code=WebsocketCloseCode.CLOSE_POLICY_VIOLATION.value, reason=verification_result.get(JwtApiResponseParams.DETAIL.value, ""))
        return
    print(f"{log_prefix} Succeeded in connecting to the websocket client - token: {verification_result}")
    user_id: str = verification_result.get(JwtParams.USER_ID.value, None)

    # Websocket Logic
    await connection_manager.connect(websocket=websocket)
    print(f"{log_prefix} Connected to the websocket client - {user_id}")
    try:
        while True:
            last_ping_time = connection_manager.active_connections.get(websocket)
            if not last_ping_time:
                break

            # timeout = last_ping_time + timedelta(seconds=10) # For Test
            timeout = last_ping_time + timedelta(minutes=1)
            now = datetime.utcnow()
            if now >= timeout:
                await websocket.close(code=WebsocketCloseCode.CLOSE_NORMAL.value, reason="Timeout due to inactivity")
                connection_manager.disconnect(websocket=websocket)
                print(f"{log_prefix} Disconnected from the websocket client - Keepalive Packet Timeout - {user_id}")
                break
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1)
                if data.lower() == "ping": # When Receiving Keepalive Packets
                    connection_manager.update_last_ping(websocket=websocket) # Extend Session Expiration
                    await websocket.send_text(data="pong") # Send a Keepalive Packet
                else:
                    await websocket.send_text(data=f"echo: {data}")
                    print(f"{log_prefix} Received data: {data}")
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket=websocket)
        print(f"{log_prefix} Disconnected from the websocket client - {user_id}")
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query, WebSocket, WebSocketDisconnect
from app.models.schemas import (
    MessageSendRequest, MessageItem, ConversationItem, ChatInitiateRequest, ChatInitiateResponse
)
from app.services.chat_service import ChatService, chat_manager
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["Private Chat & Messaging Microservice"])


def _get_current_user_or_401(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication token required to access messages.")
    user = AuthService.get_user_by_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session token. Please sign in.")
    return user


# ============================================================================
# Real-Time WebSocket Channel (/api/v1/chat/ws)
# ============================================================================
@router.websocket("/ws")
async def websocket_chat_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    Bidirectional Real-Time WebSocket for 1-to-1 Instant Messaging.
    Pushes new incoming messages to the recipient's screen with ZERO latency.
    """
    if not token:
        await websocket.close(code=1008)
        return

    user = AuthService.get_user_by_token(token)
    if not user:
        await websocket.close(code=1008)
        return

    user_id = user["id"]
    await chat_manager.connect(user_id, websocket)

    try:
        # Acknowledge connection
        await websocket.send_json({
            "type": "connection_ack",
            "user_id": user_id,
            "user_name": user["full_name"],
            "status": "connected"
        })

        while True:
            payload = await websocket.receive_json()
            event_type = payload.get("type", "chat_message")

            if event_type == "chat_message":
                receiver_id = payload.get("receiver_id")
                message_text = payload.get("message_text", "").strip()
                job_id = payload.get("job_id")

                if not receiver_id or not message_text:
                    continue

                # 1. Persist message to SQLite
                msg = ChatService.send_message(
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    message_text=message_text,
                    job_id=job_id
                )

                # 2. Push in real time to the receiver if online
                receiver_event = {
                    "type": "new_message",
                    "message": {**msg, "is_mine": False}
                }
                await chat_manager.send_to_user(receiver_id, receiver_event)

                # 3. Echo confirmation ack to sender
                sender_event = {
                    "type": "message_sent",
                    "message": {**msg, "is_mine": True}
                }
                await websocket.send_json(sender_event)

            elif event_type == "typing":
                receiver_id = payload.get("receiver_id")
                if receiver_id:
                    await chat_manager.send_to_user(receiver_id, {
                        "type": "typing",
                        "sender_id": user_id,
                        "sender_name": user["full_name"]
                    })

            elif event_type == "mark_read":
                partner_id = payload.get("partner_id")
                if partner_id:
                    ChatService.mark_thread_read(user_id, partner_id)
                    await chat_manager.send_to_user(partner_id, {
                        "type": "messages_read",
                        "reader_id": user_id
                    })

    except WebSocketDisconnect:
        chat_manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket exception for user {user_id}: {e}")
        chat_manager.disconnect(user_id, websocket)


# ============================================================================
# HTTP REST Endpoints (Parity & Fallback)
# ============================================================================
@router.get("/conversations", response_model=List[ConversationItem])
def get_my_conversations(authorization: Optional[str] = Header(None)):
    """
    Returns all active conversations belonging exclusively to the authenticated user.
    Strictly isolated: users cannot view conversations they are not part of.
    """
    user = _get_current_user_or_401(authorization)
    return ChatService.get_conversations(user["id"])


@router.get("/thread/{other_user_id}", response_model=List[MessageItem])
def get_chat_thread(other_user_id: int, authorization: Optional[str] = Header(None)):
    """
    Fetches the private 1-to-1 message thread between the current user and other_user_id.
    Zero leakage: third parties cannot see this thread.
    """
    user = _get_current_user_or_401(authorization)
    return ChatService.get_thread_messages(user["id"], other_user_id)


@router.post("/send", response_model=MessageItem)
async def send_private_message(req: MessageSendRequest, authorization: Optional[str] = Header(None)):
    """
    Sends a private message to another registered user.
    Also broadcasts to receiver's WebSocket in real time!
    """
    user = _get_current_user_or_401(authorization)
    try:
        msg = ChatService.send_message(
            sender_id=user["id"],
            receiver_id=req.receiver_id,
            message_text=req.message_text,
            job_id=req.job_id
        )

        # Broadcast in real time to receiver if they have WebSocket open
        await chat_manager.send_to_user(req.receiver_id, {
            "type": "new_message",
            "message": {**msg, "is_mine": False}
        })

        return msg
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/initiate", response_model=ChatInitiateResponse)
def initiate_chat_from_feed(req: ChatInitiateRequest, authorization: Optional[str] = Header(None)):
    """
    Resolves the target user account from a Job or Worker card and opens an instant chat thread.
    """
    user = _get_current_user_or_401(authorization)
    target_info = ChatService.get_or_create_user_for_target(req.target_type, req.target_id)
    if not target_info:
        raise HTTPException(status_code=404, detail="Target user or item not found.")
    
    if target_info["partner_id"] == user["id"]:
        raise HTTPException(status_code=400, detail="You cannot start a chat with yourself.")
        
    return target_info

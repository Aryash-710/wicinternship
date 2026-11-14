from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query
from app.models.schemas import (
    MessageSendRequest, MessageItem, ConversationItem, ChatInitiateRequest
)
from app.services.chat_service import ChatService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/chat", tags=["Private Chat & Messaging Microservice"])


def _get_current_user_or_401(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication token required to access messages.")
    user = AuthService.get_user_by_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session token. Please sign in.")
    return user


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
def send_private_message(req: MessageSendRequest, authorization: Optional[str] = Header(None)):
    """
    Sends a private message to another registered user.
    """
    user = _get_current_user_or_401(authorization)
    try:
        msg = ChatService.send_message(
            sender_id=user["id"],
            receiver_id=req.receiver_id,
            message_text=req.message_text,
            job_id=req.job_id
        )
        return msg
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/initiate")
def initiate_chat_from_feed(req: ChatInitiateRequest, authorization: Optional[str] = Header(None)):
    """
    Resolves the target user account from a Job or Worker card and opens an instant chat thread.
    """
    user = _get_current_user_or_401(authorization)
    target_info = ChatService.get_or_create_user_for_target(req.target_type, req.target_id)
    if not target_info:
        raise HTTPException(status_code=404, detail="Target user or item not found.")
    
    if target_info["other_user"]["id"] == user["id"]:
        raise HTTPException(status_code=400, detail="You cannot start a chat with yourself.")
        
    return target_info

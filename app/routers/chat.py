from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..agents import get_chat_response


router = APIRouter(prefix="", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply_text = get_chat_response(request.message)
    return ChatResponse(reply=reply_text)


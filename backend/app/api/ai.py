import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user
from app.core.response import ApiResponse, fail, success
from app.models import User
from app.schemas.ai import ChatMessage
from app.services.ai_service import chat, chat_stream

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/chat", response_model=ApiResponse, summary="聊天对话")
async def api_chat(body: ChatMessage, current_user: User = Depends(get_current_user)):
    thread_id = f"user_{current_user.id}"
    try:
        response = await chat(body.content, thread_id)
    except Exception as e:
        return fail(code=500, message=f"AI 服务异常:{e}")
    return success(data=response, message="成功")


@router.post("/chat/stream", summary="流式聊天对话(SSE)")
async def api_chat_stream(
    body: ChatMessage, current_user: User = Depends(get_current_user)
):
    thread_id = f"user_{current_user.id}"

    async def event_stream():
        try:
            async for token in chat_stream(body.content, thread_id):
                yield f"data: {json.dumps({'content': token}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

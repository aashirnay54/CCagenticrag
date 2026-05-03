import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from dependencies import get_current_user
from database import supabase
from models import ChatRequest
from services.llm_service import stream_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def chat_generator(body: ChatRequest, user_id: str):
    if body.thread_id:
        result = supabase.table("threads") \
            .select("id, title") \
            .eq("id", body.thread_id) \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        thread_id = result.data["id"]
    else:
        title = body.message[:60] + ("..." if len(body.message) > 60 else "")
        result = supabase.table("threads") \
            .insert({"user_id": user_id, "title": title}) \
            .execute()
        thread_id = result.data[0]["id"]

    supabase.table("messages").insert({
        "thread_id": thread_id,
        "user_id": user_id,
        "role": "user",
        "content": body.message,
    }).execute()

    history_result = supabase.table("messages") \
        .select("role, content") \
        .eq("thread_id", thread_id) \
        .order("created_at") \
        .execute()
    history = [{"role": m["role"], "content": m["content"]} for m in history_result.data]

    full_content = ""
    deltas = stream_chat(history, metadata={"thread_id": thread_id, "user_id": user_id})
    for delta in deltas:
        full_content += delta
        yield f"data: {json.dumps({'type': 'chunk', 'content': delta})}\n\n"

    msg_result = supabase.table("messages").insert({
        "thread_id": thread_id,
        "user_id": user_id,
        "role": "assistant",
        "content": full_content,
    }).execute()
    message_id = msg_result.data[0]["id"]

    yield f"data: {json.dumps({'type': 'done', 'thread_id': thread_id, 'message_id': message_id})}\n\n"


@router.post("")
async def chat(body: ChatRequest, user=Depends(get_current_user)):
    return StreamingResponse(
        chat_generator(body, user.id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

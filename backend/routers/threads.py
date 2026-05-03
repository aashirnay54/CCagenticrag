from fastapi import APIRouter, Depends
from dependencies import get_current_user
from database import supabase
from models import ThreadOut, ThreadCreate

router = APIRouter(prefix="/api/threads", tags=["threads"])


@router.get("", response_model=list[ThreadOut])
async def list_threads(user=Depends(get_current_user)):
    result = supabase.table("threads") \
        .select("*") \
        .eq("user_id", user.id) \
        .order("updated_at", desc=True) \
        .execute()
    return result.data


@router.post("", response_model=ThreadOut)
async def create_thread(body: ThreadCreate, user=Depends(get_current_user)):
    result = supabase.table("threads") \
        .insert({"user_id": user.id, "title": body.title}) \
        .execute()
    return result.data[0]


@router.delete("/{thread_id}", status_code=204)
async def delete_thread(thread_id: str, user=Depends(get_current_user)):
    supabase.table("threads") \
        .delete() \
        .eq("id", thread_id) \
        .eq("user_id", user.id) \
        .execute()


@router.get("/{thread_id}/messages", response_model=list)
async def list_messages(thread_id: str, user=Depends(get_current_user)):
    result = supabase.table("messages") \
        .select("*") \
        .eq("thread_id", thread_id) \
        .eq("user_id", user.id) \
        .order("created_at") \
        .execute()
    return result.data

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from database import supabase
from dependencies import get_current_user
from models import DocumentOut
from services.ingestion_service import ingest_document

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_MIME = {
    "application/pdf": "pdf",
    "text/plain": "txt",
}
MAX_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("", response_model=DocumentOut)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 50 MB limit")

    file_type = ALLOWED_MIME[file.content_type]
    user_id = str(user.id)

    doc_res = supabase.table("documents").insert({
        "user_id": user_id,
        "name": file.filename,
        "file_type": file_type,
        "source": "upload",
        "status": "pending",
    }).execute()
    doc = doc_res.data[0]
    document_id = doc["id"]

    storage_path = f"{user_id}/{document_id}/{file.filename}"
    supabase.storage.from_("documents").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": file.content_type},
    )

    supabase.table("documents").update({"storage_path": storage_path}).eq("id", document_id).execute()

    background_tasks.add_task(ingest_document, document_id, user_id, file_bytes, file_type)

    updated = supabase.table("documents").select("*").eq("id", document_id).single().execute()
    return DocumentOut(**updated.data)


@router.get("", response_model=list[DocumentOut])
def list_documents(user=Depends(get_current_user)):
    res = supabase.table("documents").select("*").eq("user_id", str(user.id)).neq("status", "deleted").order("created_at", desc=True).execute()
    return [DocumentOut(**d) for d in res.data]


@router.delete("/{document_id}")
def delete_document(document_id: str, user=Depends(get_current_user)):
    doc_res = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", str(user.id)).single().execute()
    if not doc_res.data:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = doc_res.data
    if doc.get("storage_path"):
        try:
            supabase.storage.from_("documents").remove([doc["storage_path"]])
        except Exception:
            pass

    supabase.table("documents").delete().eq("id", document_id).execute()
    return {"ok": True}

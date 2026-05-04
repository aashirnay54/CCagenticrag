import io
from pypdf import PdfReader
from database import supabase
from services.chunking_service import chunk_text
from services.embedding_service import embed_texts


def parse_file(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n\n".join(p.extract_text() or "" for p in reader.pages)
    return file_bytes.decode("utf-8", errors="replace")


def ingest_document(document_id: str, user_id: str, file_bytes: bytes, file_type: str) -> None:
    """Updates document.status at each stage — Realtime pushes changes to frontend."""
    try:
        supabase.table("documents").update({"status": "processing"}).eq("id", document_id).execute()

        text = parse_file(file_bytes, file_type)
        if not text.strip():
            raise ValueError("No extractable text — file may be a scanned PDF")

        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("Chunking produced zero chunks")

        all_embeddings = []
        for i in range(0, len(chunks), 100):
            all_embeddings.extend(embed_texts(chunks[i:i + 100]))

        supabase.table("document_chunks").delete().eq("document_id", document_id).execute()

        rows = [
            {
                "document_id": document_id,
                "user_id": user_id,
                "content": chunk,
                "chunk_index": idx,
                "embedding": emb,
            }
            for idx, (chunk, emb) in enumerate(zip(chunks, all_embeddings))
        ]
        for i in range(0, len(rows), 50):
            supabase.table("document_chunks").insert(rows[i:i + 50]).execute()

        supabase.table("documents").update(
            {"status": "completed", "chunk_count": len(chunks)}
        ).eq("id", document_id).execute()

    except Exception as e:
        supabase.table("documents").update(
            {"status": "failed", "error_message": str(e)[:500]}
        ).eq("id", document_id).execute()
        raise

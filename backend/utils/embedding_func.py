import os
import tempfile
from utils.extractor import extract_text_from_file
from utils.embedder import get_embedding
from config.supabase_client import supabase, bucket_name
from utils.chuncker import build_chunks_for_document, sha256


def embedding(document_id: str, user_id: str):
    temp_file_path = None
    try:
        response = supabase.table("documents").select("*").eq("user_id", user_id).eq("id", document_id).execute()

        if len(response.data) == 0:
            raise ValueError("Document not found")

        data = response.data[0]
        
        # Download from Storage directly to disk
        file_bytes = supabase.storage.from_(bucket_name).download(data["path"])
        
        upload_dir = '/tmp/rag_uploads'
        os.makedirs(upload_dir, exist_ok=True)
        fd, temp_file_path = tempfile.mkstemp(dir=upload_dir)
        
        with os.fdopen(fd, 'wb') as f:
            f.write(file_bytes)

        pages_text = extract_text_from_file(data["name"], temp_file_path)

        chunks = build_chunks_for_document(pages_text)

        # Optimize N+1 queries by fetching existing hashes at once
        exist_res = supabase.table("chunks").select("content_hash").eq("document_id", document_id).execute()
        existing_hashes = {row["content_hash"] for row in exist_res.data}

        nuevos_chunks = []

        for ch in chunks:
            hash = sha256(ch["content"])

            if hash in existing_hashes:
                continue

            ch["content_hash"] = hash
            nuevos_chunks.append(ch)

        if len(nuevos_chunks) == 0:
            supabase.table("documents").update({"status": "completado"}).eq("id", document_id).execute()
            return {"message": "No new chunks to embed"}

        embs = get_embedding([text["content"] for text in nuevos_chunks])

        payloads = []
        for ch, emb in zip(nuevos_chunks, embs):
            payload = {
                "embedding": emb,
                "document_id": document_id,
                "content": ch.get("content"),
                "content_hash": ch.get("content_hash"),
                "token_count": ch.get("token_count"),
                "chunk_index": ch.get("chunk_index"),
                "page": ch.get("page"),
            }

            payloads.append(payload)

        supabase.table("chunks").insert(payloads).execute()
        
        # Update document status to 'completado' on success
        supabase.table("documents").update({"status": "completado"}).eq("id", document_id).execute()

        return {"message": "Embedding successful"}

    except Exception as e:
        # Update document status to 'error' on failure
        try:
            supabase.table("documents").update({"status": "error"}).eq("id", document_id).execute()
        except Exception as db_error:
            print(f"Error updating status to error: {db_error}")
        raise e
        
    finally:
        # Clean up temporary file from disk
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

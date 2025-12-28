from utils.extractor import extract_text_from_file
from utils.embedder import get_embedding
from config.supabase_client import supabase,bucket_name
from utils.chuncker import build_chunks_for_document,sha256
from fastapi import  HTTPException  

def embedding(document_id: str,user_id: str):

  try:
    response = supabase.table("documents").select("*").eq("user_id", user_id).eq("id", document_id).execute()
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting document from Supabase: {e}")

  if len(response.data) == 0:
    raise HTTPException(status_code=404, detail="Document not found")


  data = response.data[0]  

  file_bytes = supabase.storage.from_(bucket_name).download(data["path"])

  pages_text = extract_text_from_file(data["name"], file_bytes)

  chunks = build_chunks_for_document(pages_text)

  nuevos_chunks = []

  for ch in chunks:
    hash = sha256(ch["content"])

    exist_res = supabase.table("chunks").select("*").eq("document_id", document_id).eq("content_hash", hash).execute()

    if len(exist_res.data) > 0:
      continue

    ch["content_hash"] = hash

    nuevos_chunks.append(ch)

  if len(nuevos_chunks) == 0:
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
      "chunk_index": ch.get("chunk_index") ,
      "page": ch.get("page") 
      } 
    
    payloads.append(payload)
    
  try:
    supabase.table("chunks").insert(payloads).execute()
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error saving chunk to Supabase: {e}")
  
  return {"message": "Embedding successful"}
from .supabase.client import supabase
from fastapi import HTTPException
from typing import Optional, Dict, Any
from .embedder import get_embedding
def retrieve_chunks(question: str,top_k: int = 3,document_id: Optional[str] = None) -> list[Dict[str, Any]]:
  query_embedding = get_embedding(question)

  payload = {
    "query_embedding": query_embedding,
    "match_count": top_k,
    "filter_document": document_id
  }

  try:
    response = supabase.rpc("match_chunks", payload).execute()
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting chunks from Supabase: {e}")

  return response.data
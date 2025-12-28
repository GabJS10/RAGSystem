from config.supabase_client import supabase
from fastapi import HTTPException
from typing import Optional, Dict, Any
from .embedder import get_embedding
from utils.openai import openai as client
from typing import List,Optional
def multi_query_retrieve(question: str, variants: List[str], top_k=3, document_id:Optional[str]=None, user_id:Optional[str]=None):
    # 1. Generar embeddings en batch
    queries = [question] + variants
    embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=queries
    )

    query_embeddings = [d.embedding for d in embedding_response.data]

    query_embeddings_pg = [f"[{', '.join(map(str, emb))}]" for emb in query_embeddings]

    # 2. Llamar a la función en Supabase
    response = supabase.rpc("match_chunks_multi", {
        "query_embeddings": query_embeddings_pg,
        "match_count": top_k,
        "filter_document": document_id,
        "filter_user": user_id
    }).execute()

    rows = response.data


    # 3. Deduplicar chunks
    seen = set()
    unique_chunks = []
    for row in rows:
        if row["chunk_id"] not in seen:
            seen.add(row["chunk_id"])
            unique_chunks.append(row)


    return unique_chunks

def retrieve_chunks(question: str,top_k: int = 10,document_id: Optional[str] = None,filter_user: str = None) -> list[Dict[str, Any]]:

  if filter_user is None:
    raise HTTPException(status_code=400, detail="filter_user is required")

  query_embedding = get_embedding(question)

  payload = {
    "query_embedding": query_embedding[0],
    "match_count": top_k,
    "filter_document": document_id,
    "filter_user": filter_user
  }


  try:
    response = supabase.rpc("match_chunks", payload).execute()
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting chunks from Supabase: {e}")


  if len(response.data) == 0:
    raise HTTPException(status_code=404, detail="Chunks not found")

  return response.data
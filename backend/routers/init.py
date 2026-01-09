from fastapi import APIRouter , UploadFile, HTTPException, File, Depends
from schemas.ask_schema import AskSupabaseModel
from utils.openai import openai
from config.supabase_client import supabase,bucket_name
from datetime import datetime
from utils.sanitize_filename import sanitize_filename
from schemas.embedding_schema import EmbeddingSchema
from utils.supabase_retrieve_chunks import retrieve_chunks,multi_query_retrieve
from utils.get_current_user_jwt import get_current_user_jwt
from config.tokenizer import re_rank_chunks
from config.redis_client import redis_client, queue
from rq.job import Job
from utils.embedding_func import embedding as embedding_function
from utils.messages import get_conversation,create_conversation,save_message,get_last_messages
from utils.upload_document_func import upload_document

router = APIRouter(
  prefix="/api/supabase",
  tags=["index"],
)

@router.get("/estado/{job_id}")
def estado(job_id: str):
    try:
      job = Job.fetch(job_id, connection=redis_client)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Tarea no encontrada: {e}") 
    if job.is_finished:
        return {"status": "finalizado", "resultado": job.result}
    elif job.is_failed:
        return {"status": "falló"}
    else:
        return {"status": "en proceso"}

 
@router.post("/ask-from-supabase")
async def ask_supabase(body: AskSupabaseModel, user_id: str = Depends(get_current_user_jwt)):
    from utils.rag_service import process_rag_pipeline

    result = await process_rag_pipeline(body, user_id)
    
    return result

@router.post("/embedding")
async def embedding(embedding_schema: EmbeddingSchema,user_id: str = Depends(get_current_user_jwt)):
  #get document data
  try:
     job = queue.enqueue(embedding_function, args=(embedding_schema.document_id,user_id))
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error encolando la tarea: {e}")
  return {"message": "Tarea encolada", "job_id": job.get_id()}


@router.post("/upload_document_to_supabase")
def upload_document_to_supabase(file: UploadFile = File(...),user_id: str = Depends(get_current_user_jwt)):

  #implementar jobs encolados

  try:
     job = queue.enqueue(upload_document, args=(file,user_id))
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error encolando la tarea: {e}")

  return {"message": "Tarea encolada", "job_id": job.get_id()}  
  

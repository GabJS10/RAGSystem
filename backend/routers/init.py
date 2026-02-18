from datetime import datetime
from typing import Any

from config.redis_client import queue, redis_client
from config.supabase_client import bucket_name, supabase
from config.tokenizer import re_rank_chunks
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from rq.job import Job
from schemas.ask_schema import AskSupabaseModel
from schemas.embedding_schema import EmbeddingSchema
from utils.embedding_func import embedding as embedding_function
from utils.get_current_user_jwt import get_current_user_jwt, get_current_user_ws
from utils.messages import (
    create_conversation,
    get_conversation,
    get_last_messages,
    save_message,
)
from utils.openai import openai
from utils.sanitize_filename import sanitize_filename
from utils.supabase_retrieve_chunks import multi_query_retrieve, retrieve_chunks
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
async def ask_supabase(
    body: AskSupabaseModel, user_id: str = Depends(get_current_user_jwt)
):
    from utils.rag_service import process_rag_pipeline

    result = await process_rag_pipeline(body, user_id)

    return result


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, user_id: str = Depends(get_current_user_ws)
):
    await websocket.accept()
    from utils.rag_service import process_rag_pipeline

    async def send_update(event: str, payload: Any):
        await websocket.send_json({"type": event, "data": payload})

    try:
        while True:
            data = await websocket.receive_json()
            try:
                # Validar la entrada usando el esquema existente
                body = AskSupabaseModel(**data)
            except Exception as e:
                await send_update("error", f"Datos inválidos: {e}")
                continue

            # Procesar pipeline con el callback de websocket
            res = await process_rag_pipeline(body, user_id, callback=send_update)

            await send_update("success", res)
    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            await send_update("error", str(e))
        except Exception:
            pass  # Connection likely closed


@router.post("/embedding")
async def embedding(
    embedding_schema: EmbeddingSchema, user_id: str = Depends(get_current_user_jwt)
):
    # get document data
    try:
        job = queue.enqueue(
            embedding_function, args=(embedding_schema.document_id, user_id)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encolando la tarea: {e}")
    return {"message": "Tarea encolada", "job_id": job.get_id()}


@router.post("/upload_document_to_supabase")
def upload_document_to_supabase(
    file: UploadFile = File(...), user_id: str = Depends(get_current_user_jwt)
):

    # implementar jobs encolados

    try:
        job = queue.enqueue(upload_document, args=(file, user_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encolando la tarea: {e}")

    return {"message": "Tarea encolada", "job_id": job.get_id()}

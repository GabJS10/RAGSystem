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
async def ask_supabase(body: AskSupabaseModel,user_id: str = Depends(get_current_user_jwt)):

  if body.conversation_id is None:
    conversation = await create_conversation(body.question,user_id)
    conversation_id = conversation["id"]
  else:
    conversation_id = body.conversation_id

  messages = await get_last_messages(conversation_id=conversation_id,user_id=user_id)


  if messages is None:
    context_messages = ""
  else:
    context_messages = "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in messages])


  chunks = retrieve_chunks(body.question,body.top_k,body.document_id,filter_user=user_id)

  print(chunks)

  if body.variants:
    prompt_variants = f"""
      Reformula la siguiente pregunta en 3 formas distintas, 
      manteniendo el mismo significado pero con palabras diferentes.
      Pregunta: "{body.question}"
      Devuelve solo una lista JSON de strings. Ejemplo:
      ```json
      ["Variante 1","Variante 2","Variante 3"]
      ```
    """
    
    response_variants = openai.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "Eres un asistente experto en reformular preguntas."}
        ,{"role": "user", "content": prompt_variants}],temperature=0.7
    )

    variants = response_variants.choices[0].message.content

    variants = eval(variants.split("```")[1].strip().split("json")[-1])

    if not isinstance(variants, list) or len(variants) == 0:
      raise HTTPException(status_code=500, detail="Error generating variants")

    chunks = multi_query_retrieve(body.question,variants,body.top_k,body.document_id,user_id)[:3]


  if body.re_rank:
    chunks = re_rank_chunks(body.question,chunks)


  context = "\n\n".join([chunk["content"] for chunk in chunks])

  prompt = f"""
    Context_of_previous_conversation: {context_messages}
    Main_Context: {context}
    Question: {body.question}
    Answer:
  """

  response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "Eres un asistente experto que responde usando únicamente el contexto proporcionado."}
      ,{"role": "user", "content": prompt}],temperature=0.2
  )

  answer = response.choices[0].message.content

  await save_message(message=body.question,conversation_id=conversation_id,user_id=user_id,role="user")
  await save_message(message=answer,conversation_id=conversation_id,user_id=user_id,role="assistant")

  documents_id = set([chunk["document_id"] for chunk in chunks])

  documents_name = []

  for document_id in documents_id:
    try:
      response = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", user_id).execute()
      documents_name.append(response.data[0]["name"])
    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error getting document from Supabase: {e}")
    

  return {"question": body.question, "answer": answer,"chunks":chunks,"documents":documents_name}

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
  

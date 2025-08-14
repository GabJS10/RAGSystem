from fastapi import FastAPI, UploadFile, HTTPException, File
from utils.extractor import extract_text_from_file
from utils.chuncker import chunk_text
from utils.embedder import get_embedding
from schemas.ask_schema import AskSupabaseModel
from utils.openai import openai
from utils.supabase.client import supabase,bucket_name
from datetime import datetime
from utils.sanitize_filename import sanitize_filename
from schemas.embedding_schema import EmbeddingSchema
from utils.supabase_retrieve_chunks import retrieve_chunks




#Inicialize the FastAPI app
app = FastAPI()



@app.post("/ask-from-supabase")
async def ask_supabase(body: AskSupabaseModel):
  chunks = retrieve_chunks(body.question,body.top_k,body.document_id)

  context = "\n\n".join([chunk["content"] for chunk in chunks])
  
  prompt = f"""
  Context: {context}
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

  return {"question": body.question, "answer": answer,"chunks":chunks}


@app.post("/embedding")
async def embedding(embedding_schema: EmbeddingSchema):
  #get document data

  try:
    response = supabase.table("documents").select("*").eq("id", embedding_schema.document_id).execute()
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting document from Supabase: {e}")

  data = response.data[0]  

  file_bytes = supabase.storage.from_(bucket_name).download(data["path"])

  text = extract_text_from_file(data["name"], file_bytes)


  chunks = chunk_text(text)


  try:
    for idx,chunk in enumerate(chunks):
      embedding = get_embedding(chunk)
      supabase.table("chunks").insert({
        "document_id": embedding_schema.document_id,
        "content": chunk,
        "embedding": embedding,
        "chunk_index": idx
      }).execute()
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error adding embeddings to Supabase: {e}")
  
  
  return {"message": "Embeddings added successfully"}



@app.post("/upload_document_to_supabase")
def upload_document_to_supabase(file: UploadFile = File(...)):
  storage_path = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sanitize_filename(file.filename)}"


  file_bytes = file.file.read()

  res =  supabase.storage.from_(bucket_name).upload(storage_path, file_bytes)


  if hasattr(res, "error") and res.error:
    raise HTTPException(status_code=500, detail=f"Error uploading file to Supabase: {res.error}")


  metadata = {"name": file.filename, "path": storage_path}

  query = supabase.table("documents").insert(metadata).execute()

  if hasattr(query, "error") and query.error:
    raise HTTPException(status_code=500, detail=f"Error saving metadata to Supabase: {query.error}")
  
  return {"message": "File uploaded successfully", "path": storage_path}




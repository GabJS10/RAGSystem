from fastapi import UploadFile
from datetime import datetime
from utils.sanitize_filename import sanitize_filename
from config.supabase_client import supabase,bucket_name
from fastapi import HTTPException
def upload_document(file: UploadFile, user_id: str):
  storage_path = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sanitize_filename(file.filename)}"


  file_bytes = file.file.read()

  res =  supabase.storage.from_(bucket_name).upload(storage_path, file_bytes)


  if hasattr(res, "error") and res.error:
    raise HTTPException(status_code=500, detail=f"Error uploading file to Supabase: {res.error}")


  metadata = {"name": file.filename, "path": storage_path, "user_id": user_id}

  query = supabase.table("documents").insert(metadata).execute()

  if hasattr(query, "error") and query.error:
    raise HTTPException(status_code=500, detail=f"Error saving metadata to Supabase: {query.error}")
  
  return {"message": "File uploaded successfully", "path": storage_path}


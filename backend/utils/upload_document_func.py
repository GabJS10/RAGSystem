import os
from datetime import datetime

from config.supabase_client import bucket_name, supabase
from utils.sanitize_filename import sanitize_filename


def upload_document(file_path: str, filename: str, user_id: str, document_id):
    try:
        storage_path = (
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sanitize_filename(filename)}"
        )

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        res = supabase.storage.from_(bucket_name).upload(storage_path, file_bytes)

        if hasattr(res, "error") and res.error:
            raise ValueError(f"Error uploading file to Supabase: {res.error}")

        query = (
            supabase.table("documents")
            .update({"status": "completado", "path": storage_path})
            .eq("id", document_id)
            .execute()
        )

        if hasattr(query, "error") and query.error:
            raise ValueError(f"Error updating metadata in Supabase: {query.error}")

        return {"message": "File uploaded successfully", "path": storage_path}

    except Exception as e:
        try:
            supabase.table("documents").update({"status": "error"}).eq(
                "id", document_id
            ).execute()
        except Exception as db_error:
            print(f"Error updating status to error: {db_error}")
        raise e

    finally:
        # Limpieza del archivo temporal
        if os.path.exists(file_path):
            os.remove(file_path)

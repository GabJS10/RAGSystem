from config.supabase_client import bucket_name, supabase
from fastapi import APIRouter, Depends, HTTPException
from schemas.profile import ProfileUpdateSchema
from utils.get_current_user_jwt import get_current_user_jwt

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
)


@router.get("/get-user")
def get_user(user_id: str = Depends(get_current_user_jwt)):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {e}")


@router.get("/get-documents")
def get_documents(user_id: str = Depends(get_current_user_jwt)):
    try:
        response = (
            supabase.table("documents").select("*").eq("user_id", user_id).execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting documents: {e}")


@router.put("/update-profile")
def update_profile(
    profile_data: ProfileUpdateSchema, user_id: str = Depends(get_current_user_jwt)
):
    try:
        update_data = profile_data.model_dump(mode="json", exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        response = (
            supabase.table("profiles").update(update_data).eq("id", user_id).execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404, detail="Profile not found or update failed"
            )

        return response.data[0]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {e}")


@router.delete("/delete-document/{document_id}")
def delete_document(document_id: str, user_id: str = Depends(get_current_user_jwt)):
    try:
        # Verificar que el documento pertenece al usuario
        response = (
            supabase.table("documents")
            .select("*")
            .eq("id", document_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404, detail="Documento no encontrado o no autorizado"
            )

        document = response.data[0]
        file_path = document.get("path")
        # Eliminar el archivo del Storage si tiene path
        if file_path:
            storage_response = supabase.storage.from_(bucket_name).remove([file_path])
            if hasattr(storage_response, "error") and storage_response.error:
                print(f"Error removing from storage: {storage_response.error}")
                # Puede que queramos seguir adelante y eliminar de la BD de todas formas.

        # Eliminar de la base de datos (y chunks asociados si hay borrado en cascada)
        delete_response = (
            supabase.table("documents")
            .delete()
            .eq("id", document_id)
            .eq("user_id", user_id)
            .execute()
        )

        if hasattr(delete_response, "error") and delete_response.error:
            raise HTTPException(
                status_code=500,
                detail=f"Error eliminando metadatos: {delete_response.error}",
            )

        return {"message": "Documento eliminado con éxito"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando documento: {e}")

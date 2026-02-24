from config.supabase_client import supabase
from fastapi import APIRouter, Depends, HTTPException
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

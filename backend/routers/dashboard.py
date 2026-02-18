from config.supabase_client import supabase
from fastapi import HTTPException,APIRouter, Depends
from utils.get_current_user_jwt import get_current_user_jwt


router = APIRouter(
  prefix="/api/dashboard",
  tags=["dashboard"],
)


@router.get("/get-documents")
def get_documents(user_id: str = Depends(get_current_user_jwt)):
  try:
    response = supabase.table("documents").select("*").eq("user_id", user_id).execute()
    return response.data
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting documents: {e}")
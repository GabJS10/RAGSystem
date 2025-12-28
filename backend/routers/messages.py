from config.supabase_client import supabase
from fastapi import HTTPException,APIRouter, Depends
from schemas.messages_schema import GetMessagesSchema
from utils.get_current_user_jwt import get_current_user_jwt


router = APIRouter(
  prefix="/api/messages",
  tags=["messages"],
)

@router.post("/get-messages")
def get_messages(body: GetMessagesSchema,user_id: str = Depends(get_current_user_jwt)):

  try:
    response = supabase.table("messages").select("*").eq("conversation_id", body.conversation_id).order("created_at", desc=True).execute()
    return response.data
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting messages: {e}")
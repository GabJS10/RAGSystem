from config.supabase_client import supabase
from fastapi import HTTPException,Depends
from typing import Literal
async def create_conversation(title: str = "Nueva conversación",user_id: str = None):
  if user_id is None:
      raise HTTPException(status_code=400, detail="user_id is required")
  
  try:
    response = supabase.table("conversations").insert({"title": title, "user_id": user_id}).execute()
    return response.data[0]
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error creating conversation: {e}")

async def save_message(message: str,conversation_id: str,user_id: str = None, role: Literal["user","assistant"] = "user"):

  print(role)

  if user_id is None: 
    raise HTTPException(status_code=400, detail="user_id is required")
  try:
    response = supabase.table("messages").insert({"content": message, "conversation_id": conversation_id, "role" : role}).execute()
    return response.data[0]
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error saving message: {e}")
  
async def get_conversation(conversation_id: str,user_id: str = None ):
  
  if user_id is None: 
    raise HTTPException(status_code=400, detail="user_id is required")
  
  try:
    response = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user_id).execute()
    return response.data[0]
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting conversation: {e}")
  

async def get_all_conversations(user_id: str = None):
  
  if user_id is None: 
    raise HTTPException(status_code=400, detail="user_id is required")
  
  try:
    response = supabase.table("conversations").select("*").eq("user_id", user_id).execute()
    return response.data
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting conversations: {e}")
  
async def get_last_messages(conversation_id: str,user_id: str = None,limit: int = 10):
  
  if user_id is None: 
    raise HTTPException(status_code=400, detail="user_id is required")
  try:
    response = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=True).limit(limit).execute()
    return response.data
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error getting last messages: {e}")
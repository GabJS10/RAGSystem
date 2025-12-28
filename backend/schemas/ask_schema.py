from pydantic import BaseModel
from typing import Optional

class AskSupabaseModel(BaseModel):
  question: str
  top_k: int = 10 
  document_id: Optional[str] = None 
  re_rank: bool = False
  variants:bool = False
  conversation_id: Optional[str] = None


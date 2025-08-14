from pydantic import BaseModel
from typing import Optional



class AskSupabaseModel(BaseModel):
  question: str
  top_k: int = 3 
  document_id: Optional[str] = None  
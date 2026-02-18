from typing import Optional

from pydantic import BaseModel


class AskSupabaseModel(BaseModel):
    question: str
    top_k: int = 15
    document_id: Optional[str] = None
    re_rank: bool = False
    variants: bool = False
    conversation_id: Optional[str] = None

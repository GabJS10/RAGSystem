from pydantic import BaseModel

class AskModel(BaseModel):
  question: str
  top_k: int = 3
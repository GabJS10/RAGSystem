from pydantic import BaseModel

class EmbeddingSchema(BaseModel):
  document_id: str
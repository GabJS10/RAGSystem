from pydantic import BaseModel

class GetMessagesSchema(BaseModel):
  conversation_id: str
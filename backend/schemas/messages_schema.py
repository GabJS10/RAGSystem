from pydantic import BaseModel


class GetMessagesSchema(BaseModel):
    conversation_id: str


class CreateConversationSchema(BaseModel):
    question: str

from pydantic import BaseModel
class signupSchema(BaseModel):
  email: str
  password: str

class singinSchema(BaseModel):
  email: str
  password: str
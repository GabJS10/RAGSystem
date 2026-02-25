from typing import Optional
from datetime import date
from pydantic import BaseModel

class ProfileUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    avatar_url: Optional[str] = None

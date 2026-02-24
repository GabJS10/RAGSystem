from datetime import date

from pydantic import BaseModel


class signupSchema(BaseModel):
    email: str
    password: str
    first_name: str
    birth_date: date


class singinSchema(BaseModel):
    email: str
    password: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str

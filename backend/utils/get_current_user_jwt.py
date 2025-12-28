import jwt
from config.supabase_client import supabase_jwt_secret
from fastapi import HTTPException,Header


async def get_current_user_jwt(authorization: str = Header(...)):
  if not authorization.startswith("Bearer "):
    raise HTTPException(status_code=401, detail="Invalid authorization header")
  
  token = authorization.split(" ")[1]
  try:  
    payload = jwt.decode(token, supabase_jwt_secret, algorithms=["HS256"], options={"require": ["exp","sub"]},audience="authenticated")
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Token expired")
  except jwt.InvalidTokenError as e:
    raise HTTPException(status_code=401, detail=f"Invalid token {e}")

  return payload["sub"]
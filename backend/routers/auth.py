from config.supabase_client import supabase
from fastapi import HTTPException,APIRouter
from schemas.auth import signupSchema,singinSchema

router = APIRouter(
  prefix="/api/auth",
  tags=["auth"],
)

@router.post("/register")
async def signup(body: signupSchema):
  try:
    response = supabase.auth.sign_up({
      "email": body.email,
      "password": body.password
    })
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error signing up: {e}")

  return {"message": "Signup successful","response": response}


@router.post("/login")
async def login(body: singinSchema):
  try:
    response = supabase.auth.sign_in_with_password({
      "email": body.email,
      "password": body.password
    })
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error logging in: {e}")

  return {"message": "Login successful","response": response}
  

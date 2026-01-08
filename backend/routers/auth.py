from config.supabase_client import supabase
from fastapi import HTTPException,APIRouter
from schemas.auth import signupSchema,singinSchema,RefreshTokenSchema


router = APIRouter(
  prefix="/api/auth",
  tags=["auth"],
)

@router.post("/register")
async def signup(body: signupSchema):
  try:
    supabase.auth.sign_up({
      "email": body.email,
      "password": body.password
    })
  except Exception as e:
    print(e)
    raise HTTPException(status_code=400, detail=f"{e}")


  return {"message": "Signup successful" }


@router.post("/login")
async def login(body: singinSchema):

  print("estoy aqui")

  try:
    response = supabase.auth.sign_in_with_password({
      "email": body.email,
      "password": body.password
    })
  except Exception as e:
    raise HTTPException(status_code=400, detail=f"{e}")

  print(response.session.access_token)


  return {"message": "Login successful","access_token":response.session.access_token,"refresh_token":response.session.refresh_token}


@router.post("/refresh-token")
async def refresh_token(body: RefreshTokenSchema):
  try:
    response = supabase.auth.refresh_session(body.refresh_token)
    return {
      "access_token": response.session.access_token,
      "refresh_token": response.session.refresh_token
    }
  except Exception as e:
    raise HTTPException(status_code=401, detail="Invalid refresh token")
  

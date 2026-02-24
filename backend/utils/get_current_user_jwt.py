import jwt
from config.supabase_client import supabase_jwt_secret
from fastapi import Header, HTTPException, Query, WebSocketException, status


def validate_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            supabase_jwt_secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
            audience="authenticated",
        )
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token {e}")


async def get_current_user_jwt(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    try:
        return validate_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


async def get_current_user_ws(token: str = Query(...)):
    try:
        return validate_token(token)
    except ValueError as e:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))

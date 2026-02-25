from config.supabase_client import supabase
from fastapi import APIRouter, Depends, HTTPException
from utils.get_current_user_jwt import get_current_user_jwt
from schemas.profile import ProfileUpdateSchema

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
)


@router.get("/get-user")
def get_user(user_id: str = Depends(get_current_user_jwt)):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {e}")


@router.get("/get-documents")
def get_documents(user_id: str = Depends(get_current_user_jwt)):
    try:
        response = (
            supabase.table("documents").select("*").eq("user_id", user_id).execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting documents: {e}")


@router.put("/update-profile")
def update_profile(
    profile_data: ProfileUpdateSchema, user_id: str = Depends(get_current_user_jwt)
):
    try:
        update_data = profile_data.model_dump(mode="json", exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        response = (
            supabase.table("profiles").update(update_data).eq("id", user_id).execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404, detail="Profile not found or update failed"
            )

        return response.data[0]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {e}")


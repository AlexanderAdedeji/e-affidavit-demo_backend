from fastapi import APIRouter, Depends

from app.api.dependencies.authentication import get_currently_authenticated_user


router = APIRouter()




@router.get("/user_default")
def user_default(current_user= Depends(get_currently_authenticated_user)):
    return {"msg":"User default"}
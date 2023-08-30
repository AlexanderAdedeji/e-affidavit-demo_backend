from fastapi import APIRouter
from app.api.routers import user_routes, authentication_route

router = APIRouter()


router.include_router(
    authentication_route.router, tags=["Authentication"], prefix="/auth"
)
router.include_router(user_routes.router, tags=["Users"], prefix="/user")

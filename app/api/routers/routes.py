from fastapi import APIRouter
from app.api.routers import (
    user_routes,
    authentication_route,
    user_type_routes,
    attestation_route,
    document_route,
)

router = APIRouter()


router.include_router(
    authentication_route.router, tags=["Authentication"], prefix="/auth"
)
router.include_router(user_routes.router, tags=["Users"], prefix="/user")
router.include_router(user_type_routes.router, tags=["User Type"], prefix="/user_type")
router.include_router(
    attestation_route.router, tags=["Attestations"], prefix="/attestation"
)
router.include_router(document_route.router, tags=["Documents"], prefix="/document")




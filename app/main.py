from fastapi import FastAPI, APIRouter
from app.api.routers.routes import router as global_router
from app.database.session import create_session, engine
from starlette.middleware.cors import CORSMiddleware
import starlette.responses as _responses
from app.core.settings.config import Settings
from app.database.base import Base



Base.metadata.create_all(bind=engine)
origins = ["https://e-affidavit.vercel.app/","https://e-affidavit.vercel.app"]

settings= Settings()


def create_application_instance() -> FastAPI:
    application = FastAPI(title=settings.PROJECT_NAME)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(global_router, prefix=settings.API_URL_PREFIX)
    return application


app = create_application_instance()








@app.get("/")
async def root():
    return _responses.RedirectResponse("/docs")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings.config import settings





def create_database_engine():
    if settings.DEBUG:
        url = settings.DEVELOPMENT_DATABASE_URL
    else:
        url = settings.PRODUCTION_DATABASE_URL
    return create_engine(url, pool_pre_ping=True)


engine = create_database_engine()
def create_session():
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

SessionLocal = create_session()

from sqlmodel import SQLModel, create_engine
from .config import get_settings

engine = None

async def startup():
    global engine
    settings = get_settings()
    engine = create_engine(str(settings.database_url), echo=settings.debug)
    # Para MVP, criar tabelas automaticamente (substituir por Alembic depois)
    SQLModel.metadata.create_all(engine)

async def shutdown():
    pass

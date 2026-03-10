import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Obtener URL de base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear engine de conexión
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Crear sesión de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos ORM
Base = declarative_base()

# Dependencia para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
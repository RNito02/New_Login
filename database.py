from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Configuración de la base de datos PostgreSQL
DATABASE_URL = "postgresql://postgres:12345@localhost/Login"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear instancia de la aplicación FastAPI
app = FastAPI()


# Modelos SQLAlchemy
Base = declarative_base()

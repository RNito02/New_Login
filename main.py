from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime
from schemas import EmpleadoCreate, UserCreate, UserLogin
from database import SessionLocal, engine
from models import Empleado, User
from database import Base


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/empleados/", response_model=EmpleadoCreate)
def create_empleado(empleado: EmpleadoCreate):
    db = SessionLocal()

    # Verificar si el empleado ya existe
    existing_empleado = db.query(Empleado).filter(
        Empleado.num_nomina == empleado.num_nomina).first()
    if existing_empleado:
        db.close()
        raise HTTPException(status_code=400, detail="El empleado ya existe")

    # Validar que la fecha_ingreso sea una fecha pasada
    fecha_ingreso = datetime.strptime(
        empleado.fecha_ingreso, "%Y-%m-%d").date()
    today = datetime.now().date()
    if fecha_ingreso >= today:
        db.close()
        raise HTTPException(
            status_code=400, detail="La fecha de ingreso debe ser una fecha pasada")

    db_empleado = Empleado(**empleado.dict())
    db.add(db_empleado)
    db.commit()
    db.refresh(db_empleado)
    db.close()
    return db_empleado


@app.get("/empleados/{num_nomina}", response_model=EmpleadoCreate)
def read_empleado(num_nomina: str):
    db = SessionLocal()
    empleado = db.query(Empleado).filter(
        Empleado.num_nomina == num_nomina).first()
    db.close()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

# CRUD para User


@app.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate):
    db = SessionLocal()

    # Verificar si el empleado existe
    empleado = db.query(Empleado).filter(
        Empleado.num_nomina == user.num_nomina).first()
    if empleado is None:
        db.close()
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Verificar si ya existe un usuario con el mismo número de nómina
    existing_user = db.query(User).filter(
        User.num_nomina == user.num_nomina).first()
    if existing_user:
        db.close()
        raise HTTPException(
            status_code=400, detail="Ya existe un usuario con este número de nómina")

    # Hash de la contraseña antes de almacenarla en la base de datos
    hashed_password = pwd_context.hash(user.hashed_password)

    db_user = User(num_nomina=user.num_nomina,
                   hashed_password=hashed_password, rol_user=user.rol_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user


@app.get("/users/{id}", response_model=UserCreate)
def read_user(id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == id).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Ruta para iniciar sesión


@app.post("/login/")
def login(user_data: UserLogin):
    db = SessionLocal()
    user = db.query(User).filter(User.num_nomina ==
                                 user_data.num_nomina).first()
    db.close()

    if user is None or not user.verify_password(user_data.hashed_password):
        raise HTTPException(
            status_code=401, detail="Número de nómina o contraseña incorrectos")

    # En este punto, el usuario ha iniciado sesión con éxito
    # Puedes implementar la lógica adicional que necesites, como generar un token de acceso, etc.

    return {"message": "Inicio de sesión exitoso"}

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime

# Configuración de la base de datos PostgreSQL
DATABASE_URL = "postgresql://postgres:12345@localhost/Login"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear instancia de la aplicación FastAPI
app = FastAPI()

# Configuración para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos SQLAlchemy
Base = declarative_base()


class Empleado(Base):
    __tablename__ = "empleados"

    num_nomina = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, index=True)
    jefe_directo = Column(String, index=True)
    departamento = Column(String, index=True)
    fecha_ingreso = Column(String, index=True)
    is_active = Column(Boolean, default=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    num_nomina = Column(Integer, ForeignKey("empleados.num_nomina"))
    rol_user = Column(String, index=True)
    hashed_password = Column(String, index=True)

    # Método para verificar la contraseña

    def verify_password(self, hashed_password: str):
        return pwd_context.verify(hashed_password, self.hashed_password)


# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Esquemas Pydantic


class EmpleadoCreate(BaseModel):
    num_nomina: int
    nombre: str
    email: str
    jefe_directo: str
    departamento: str
    fecha_ingreso: str
    is_active: bool


class UserCreate(BaseModel):
    num_nomina: int
    rol_user: str
    hashed_password: str

# CRUD para Empleado


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
def login(user_data: UserCreate):
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

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from database import Base


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

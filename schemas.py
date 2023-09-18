from pydantic import BaseModel

# Todo el schema de empleado


class EmpleadoCreate(BaseModel):
    num_nomina: int
    nombre: str
    email: str
    jefe_directo: str
    departamento: str
    fecha_ingreso: str
    is_active: bool


# Todo el schema de User
class UserCreate(BaseModel):
    num_nomina: int
    rol_user: str
    hashed_password: str


# Todo el schema de Login
class UserLogin(BaseModel):
    num_nomina: int
    hashed_password: str

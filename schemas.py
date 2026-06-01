from pydantic import BaseModel, EmailStr
from models import RolUsuario
from datetime import datetime

# --- ESQUEMAS PARA USUARIOS ---

class UsuarioLogin(BaseModel):
    correo_institucional: EmailStr
    password: str

class UsuarioResponse(BaseModel):
    id: int
    rut: str
    correo_institucional: EmailStr
    rol: RolUsuario

    class Config:
        from_attributes = True

# --- ESQUEMAS PARA ASIGNACIONES (Rotativas) ---

class AsignacionBase(BaseModel):
    estudiante_id: int
    centro_id: int
    fecha_inicio_rotativa: datetime
    fecha_fin_rotativa: datetime

class AsignacionCreate(AsignacionBase):
    pass

class AsignacionResponse(AsignacionBase):
    id: int

    class Config:
        from_attributes = True      
         
# --- ESQUEMAS PARA GEOCERCAS (Centros Clínicos) ---

class CentroClinicoBase(BaseModel):
    nombre: str
    latitud: float
    longitud: float
    radio_permitido: int # En metros, ej: 200

class CentroClinicoCreate(CentroClinicoBase):
    pass

class CentroClinicoResponse(CentroClinicoBase):
    id: int

    class Config:
        from_attributes = True # <-- Esto es lo que faltaba

# --- ESQUEMAS PARA ASISTENCIA (Marcaje GPS) ---

class RegistroEntrada(BaseModel):
    asignacion_id: int
    latitud_actual: float
    longitud_actual: float

# --- ESQUEMAS PARA EL TUTOR (Validación) ---

class ValidarAsistencia(BaseModel):
    registro_id: int
    aprobar: bool # True para validar, False para rechazar

# --- ESQUEMAS PARA SALIDA (Cierre de Turno Simplificado) ---

class RegistroSalida(BaseModel):
    registro_id: int
    latitud_actual: float
    longitud_actual: float
    justificacion: str | None = None # Campo de texto libre opcional
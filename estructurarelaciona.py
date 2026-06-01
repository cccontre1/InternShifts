from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

# Instancia base para definir las tablas
Base = declarative_base()

# ==========================================
# 1. DEFINICIÓN ESTRICTA DE ETIQUETAS (Data Governance)
# ==========================================
# Esto asegura que jamás entre un dato con mayúsculas mezcladas o errores.
class RolUsuario(enum.Enum):
    estudiante = "estudiante"
    tutor = "tutor"
    coordinador = "coordinador"

class EstadoAsistencia(enum.Enum):
    pendiente = "pendiente"
    validado_tutor = "validado_tutor"
    rechazado = "rechazado"
    turno_extra = "turno_extra"
    salida_tardia = "salida_tardia"

# ==========================================
# 2. MODELOS RELACIONALES (Las Tablas)
# ==========================================

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, index=True, nullable=False)
    correo_institucional = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False)
    
    # Relaciones
    asignaciones = relationship("Asignacion", back_populates="estudiante")

class CentroClinico(Base):
    __tablename__ = "centros_clinicos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    radio_permitido = Column(Integer, nullable=False) # En metros (ej: 200)
    
    # Relaciones
    asignaciones = relationship("Asignacion", back_populates="centro")

class Asignacion(Base):
    __tablename__ = "asignaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    centro_id = Column(Integer, ForeignKey("centros_clinicos.id"), nullable=False)
    fecha_inicio_rotativa = Column(DateTime, nullable=False)
    fecha_fin_rotativa = Column(DateTime, nullable=False)
    
    # Relaciones bidireccionales
    estudiante = relationship("Usuario", back_populates="asignaciones")
    centro = relationship("CentroClinico", back_populates="asignaciones")
    registros = relationship("RegistroAsistencia", back_populates="asignacion")

class RegistroAsistencia(Base):
    __tablename__ = "registros_asistencia"
    
    id = Column(Integer, primary_key=True, index=True)
    asignacion_id = Column(Integer, ForeignKey("asignaciones.id"), nullable=False)
    
    # El timestamp captura la hora exacta del servidor, evitando manipulación
    timestamp_entrada = Column(DateTime, default=datetime.utcnow)
    timestamp_salida = Column(DateTime, nullable=True)
    
    # Las coordenadas reales desde donde el alumno presionó el botón
    latitud_real = Column(Float, nullable=False)
    longitud_real = Column(Float, nullable=False)
    
    # El estado estandarizado para entrenar el modelo futuro
    estado_validacion = Column(Enum(EstadoAsistencia), default=EstadoAsistencia.pendiente)
    motivo_excepcion = Column(String, nullable=True) # Solo se llena en turnos extra
    
    # Relaciones
    asignacion = relationship("Asignacion", back_populates="registros")
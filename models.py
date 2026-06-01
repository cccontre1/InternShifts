from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class RolUsuario(str, enum.Enum):
    estudiante = "estudiante"
    tutor = "tutor"
    coordinador = "coordinador"

class EstadoAsistencia(str, enum.Enum):
    pendiente = "pendiente"
    validado_tutor = "validado_tutor"
    rechazado = "rechazado"
    turno_extra = "turno_extra"
    salida_tardia = "salida_tardia"
    salida_anticipada = "salida_anticipada"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, index=True, nullable=False)
    correo_institucional = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(SQLEnum(RolUsuario), nullable=False)
    asignaciones = relationship("Asignacion", back_populates="estudiante")

class CentroClinico(Base):
    __tablename__ = "centros_clinicos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    radio_permitido = Column(Integer, nullable=False)
    asignaciones = relationship("Asignacion", back_populates="centro")

class Asignacion(Base):
    __tablename__ = "asignaciones"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    centro_id = Column(Integer, ForeignKey("centros_clinicos.id"), nullable=False)
    fecha_inicio_rotativa = Column(DateTime, nullable=False)
    fecha_fin_rotativa = Column(DateTime, nullable=False)
    estudiante = relationship("Usuario", back_populates="asignaciones")
    centro = relationship("CentroClinico", back_populates="asignaciones")
    registros = relationship("RegistroAsistencia", back_populates="asignacion")

class RegistroAsistencia(Base):
    __tablename__ = "registros_asistencia"
    id = Column(Integer, primary_key=True, index=True)
    asignacion_id = Column(Integer, ForeignKey("asignaciones.id"), nullable=False)
    timestamp_entrada = Column(DateTime, default=datetime.utcnow)
    timestamp_salida = Column(DateTime, nullable=True)
    latitud_real = Column(Float, nullable=False)
    longitud_real = Column(Float, nullable=False)
    estado_validacion = Column(SQLEnum(EstadoAsistencia), default=EstadoAsistencia.pendiente)
    motivo_excepcion = Column(String, nullable=True)
    asignacion = relationship("Asignacion", back_populates="registros")
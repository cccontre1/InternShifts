from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime
import models, schemas
import math

router = APIRouter(
    prefix="/asistencia",
    tags=["Control de Asistencia y GPS"]
)

# Motor Matemático: Fórmula de Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371000  # Radio de la Tierra en metros
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi_1) * math.cos(phi_2) * \
        math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c # Devuelve la distancia exacta en metros

# Endpoint para presionar el botón "Iniciar Turno" (RF-02)
@router.post("/entrada", status_code=status.HTTP_201_CREATED)
def registrar_entrada(registro: schemas.RegistroEntrada, db: Session = Depends(get_db)):
    # 1. Buscamos la asignación para saber a qué hospital debería ir
    asignacion = db.query(models.Asignacion).filter(models.Asignacion.id == registro.asignacion_id).first()
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    # 2. Rescatamos los datos del hospital oficial
    centro = asignacion.centro
    
    # 3. Calculamos la distancia entre el celular y el hospital
    distancia = calcular_distancia(
        registro.latitud_actual, registro.longitud_actual,
        centro.latitud, centro.longitud
    )
    
    # 4. Lógica de Geocerca (Bloqueo Antifraude)
    if distancia > centro.radio_permitido:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Intento bloqueado. Estás a {int(distancia)} metros del centro. Debes estar a menos de {centro.radio_permitido} metros para iniciar el turno."
        )
    
    # 5. Si está dentro del radio, guardamos el registro en la Base de Datos
    nuevo_registro = models.RegistroAsistencia(
        asignacion_id=registro.asignacion_id,
        latitud_real=registro.latitud_actual,
        longitud_real=registro.longitud_actual,
        estado_validacion=models.EstadoAsistencia.pendiente # Etiqueta estricta inyectada
    )
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    
    return {
        "mensaje": "Turno iniciado correctamente", 
        "distancia_calculada_metros": int(distancia),
        "registro_id": nuevo_registro.id
    }
# Endpoint para el Panel del Tutor (RF-05 / RF-06)
@router.patch("/validar", status_code=status.HTTP_200_OK)
def validar_asistencia(payload: schemas.ValidarAsistencia, db: Session = Depends(get_db)):
    # 1. Buscamos el registro de asistencia que el tutor quiere evaluar
    registro = db.query(models.RegistroAsistencia).filter(models.RegistroAsistencia.id == payload.registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
    
    # 2. Cambiamos el estado según la decisión del tutor usando los Enums
    if payload.aprobar:
        registro.estado_validacion = models.EstadoAsistencia.validado_tutor
    else:
        registro.estado_validacion = models.EstadoAsistencia.rechazado
        
    db.commit()
    db.refresh(registro)
    
    return {
        "mensaje": f"El registro {registro.id} ha sido actualizado con éxito.",
        "nuevo_estado": registro.estado_validacion
    }    

# Endpoint Simplificado para Finalizar Turno (RF-02)
@router.post("/salida", status_code=status.HTTP_200_OK)
def registrar_salida(registro_input: schemas.RegistroSalida, db: Session = Depends(get_db)):
    # 1. Buscamos el turno activo
    registro = db.query(models.RegistroAsistencia).filter(
        models.RegistroAsistencia.id == registro_input.registro_id,
        models.RegistroAsistencia.timestamp_salida == None
    ).first()
    
    if not registro:
        raise HTTPException(
            status_code=404, 
            detail="No se encontró un turno activo para este Registro ID, o ya fue cerrado."
        )
    
    # 2. Validación de Geocerca de Salida (Mantenemos la seguridad antifraude)
    centro = registro.asignacion.centro
    distancia_salida = calcular_distancia(
        registro_input.latitud_actual, registro_input.longitud_actual,
        centro.latitud, centro.longitud
    )
    
    if distancia_salida > centro.radio_permitido:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Bloqueo de salida: Debes estar en el centro clínico para cerrar el turno. Estás a {int(distancia_salida)} metros."
        )
    
    # 3. Registramos la hora de salida y guardamos la justificación si existe
    registro.timestamp_salida = datetime.utcnow()
    registro.motivo_excepcion = registro_input.justificacion # Guardamos el texto libre
    
    # 4. Calculamos las horas reales trabajadas para el reporte
    delta_tiempo = registro.timestamp_salida - registro.timestamp_entrada
    horas_trabajadas = delta_tiempo.total_seconds() / 3600.0
    
    # El estado simplemente queda en 'pendiente' para revisión del tutor
    registro.estado_validacion = models.EstadoAsistencia.pendiente
    
    db.commit()
    db.refresh(registro)
    
    return {
        "mensaje": "Turno finalizado correctamente",
        "horas_totales_registradas": round(horas_trabajadas, 4),
        "justificacion_ingresada": registro.motivo_excepcion,
        "estado": registro.estado_validacion
    }
    
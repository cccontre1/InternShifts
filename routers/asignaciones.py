from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(
    prefix="/asignaciones",
    tags=["Gestión de Asignaciones (Rotativas)"]
)

@router.post("/", response_model=schemas.AsignacionResponse, status_code=status.HTTP_201_CREATED)
def crear_asignacion(asignacion: schemas.AsignacionCreate, db: Session = Depends(get_db)):
    # 1. Verificamos que el estudiante exista
    estudiante = db.query(models.Usuario).filter(models.Usuario.id == asignacion.estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado en la base de datos")
    
    # 2. Verificamos que el Centro Clínico exista
    centro = db.query(models.CentroClinico).filter(models.CentroClinico.id == asignacion.centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro Clínico no encontrado en la base de datos")

    # 3. Si ambos existen, creamos el cruce
    nueva_asignacion = models.Asignacion(**asignacion.model_dump())
    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)
    return nueva_asignacion
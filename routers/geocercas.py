from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

# Creamos el enrutador específico para las geocercas
router = APIRouter(
    prefix="/geocercas",
    tags=["Gestión de Geocercas (Centros Clínicos)"]
)

# Ruta para crear un nuevo hospital / centro de práctica (RF-07)
@router.post("/", response_model=schemas.CentroClinicoResponse, status_code=status.HTTP_201_CREATED)
def crear_centro_clinico(centro: schemas.CentroClinicoCreate, db: Session = Depends(get_db)):
    # Desempaquetamos los datos validados y los pasamos al modelo de SQLAlchemy
    nuevo_centro = models.CentroClinico(**centro.model_dump())
    db.add(nuevo_centro)
    db.commit()
    db.refresh(nuevo_centro)
    return nuevo_centro

# Ruta para ver la lista de todos los centros creados
@router.get("/", response_model=list[schemas.CentroClinicoResponse])
def listar_centros(db: Session = Depends(get_db)):
    centros = db.query(models.CentroClinico).all()
    return centros
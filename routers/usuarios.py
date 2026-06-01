from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

# Creamos el enrutador específico para esta sección
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios y Autenticación"]
)

@router.post("/login", response_model=schemas.UsuarioResponse)
def login(credenciales: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    usuario_db = db.query(models.Usuario).filter(models.Usuario.correo_institucional == credenciales.correo_institucional).first()
    
    if not usuario_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    if usuario_db.password_hash != credenciales.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")
    
    return usuario_db

@router.post("/prueba", response_model=schemas.UsuarioResponse)
def crear_usuario_prueba(db: Session = Depends(get_db)):
    nuevo_usuario = models.Usuario(
        rut="12345678-9",
        correo_institucional="alumno@universidad.cl",
        password_hash="clave123",
        rol=models.RolUsuario.estudiante
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario
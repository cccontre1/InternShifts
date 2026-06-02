from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware # IMPORTACIÓN NUEVA
from sqlalchemy.orm import Session 
from database import engine, Base
from database import get_db
import models
from routers import usuarios, geocercas, asignaciones, asistencia, coordinador 

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="InternShifts API",
    description="API modular para trazabilidad clínica e inteligencia analítica",
    version="1.0.0"
)

# ==========================================
# CONFIGURACIÓN DE CORS (Pase de movilidad para el Frontend)
# ==========================================
# Esto permite que tu futura app móvil o web se conecte al backend sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se cambia "*" por la URL de tu app. Para pruebas permite todo.
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PATCH, DELETE, etc.
    allow_headers=["*"], # Permite cualquier cabecera de seguridad
)

# Conexión de rutas (Enrutadores)
app.include_router(usuarios.router)
app.include_router(geocercas.router)
app.include_router(asignaciones.router)
app.include_router(asistencia.router)
app.include_router(coordinador.router)


@app.get("/")
def read_root():
    return {"mensaje": "Servidor InternShifts operando con arquitectura modular y CORS habilitado"}

@app.post("/geocercas/calibrar-prueba")
def calibrar_hospital_prueba(datos: dict, db: Session = Depends(get_db)):
    """
    Toma las coordenadas del desarrollador y mueve el Centro Clínico ID 1 
    a esa ubicación exacta para facilitar las pruebas del equipo.
    """
    # Cambiado a models.CentroClinico para que coincida con tus modelos reales
    hospital = db.query(models.CentroClinico).filter(models.CentroClinico.id == 1).first()
    
    if not hospital:
        return {"error": "No se encontró el centro clínico base. Ejecuta seed.py primero."}
    
    # Sobrescribimos su ubicación con la de la persona que está probando
    hospital.latitud = datos["latitud"]
    hospital.longitud = datos["longitud"]
    hospital.nombre = "Hospital de Prueba (Calibrado)"
    
    db.commit()
    return {"mensaje": "Base de datos calibrada con tu ubicación actual con éxito."}
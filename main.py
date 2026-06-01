from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # IMPORTACIÓN NUEVA
from database import engine
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
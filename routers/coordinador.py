from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
import models
import csv
import io

router = APIRouter(
    prefix="/coordinador",
    tags=["Panel del Coordinador (Reportes)"]
)

# Endpoint para descargar el reporte transaccional en CSV (RF-09)
@router.get("/reporte-csv")
def descargar_reporte_csv(db: Session = Depends(get_db)):
    # 1. Traemos todos los registros de asistencia de la base de datos
    registros = db.query(models.RegistroAsistencia).all()
    
    # 2. Creamos un archivo virtual de texto en memoria
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';') # Separador por punto y coma (ideal para Excel en Latam)
    
    # 3. Escribimos las cabeceras del reporte
    writer.writerow(["ID Registro", "RUT Estudiante", "Centro Clinico", "Fecha/Hora Entrada", "Fecha/Hora Salida", "Latitud Real", "Longitud Real", "Estado Validacion"])
    
    # 4. Poblamos el CSV cruzando las relaciones de la base de datos
    for r in registros:
        # Extraemos de forma segura los datos de las tablas relacionadas
        rut_estudiante = r.asignacion.estudiante.rut if r.asignacion and r.asignacion.estudiante else "N/A"
        nombre_centro = r.asignacion.centro.nombre if r.asignacion and r.asignacion.centro else "N/A"
        
        writer.writerow([
            r.id,
            rut_estudiante,
            nombre_centro,
            r.timestamp_entrada.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp_entrada else "",
            r.timestamp_salida.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp_salida else "En turno",
            r.latitud_real,
            r.longitud_real,
            r.estado_validacion.value
        ])
    
    # Reposicionamos el puntero del archivo al inicio
    output.seek(0)
    
    # 5. Retornamos el archivo como un flujo descargable
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reporte_asistencia_internshifts.csv"}
    )
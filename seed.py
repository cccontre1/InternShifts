from database import SessionLocal, engine
import models
from datetime import datetime
import os

def limpiar_y_poblar():
    # 1. Eliminar la base de datos antigua si existe para partir 100% de cero
    if os.path.exists("internshifts.db"):
        print("🗑️  Eliminando base de datos antigua...")
        # Cerramos conexiones activas antes de borrar
        engine.dispose()
        try:
            os.remove("internshifts.db")
        except PermissionError:
            print("⚠️ No se pudo eliminar el archivo .db directamente porque está en uso. Limpiando tablas internamente...")

    print("🏗️  Creando nuevas tablas limpias...")
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("🌱 Iniciando la carga de datos de prueba (Seeding)...")

        # 2. CREACIÓN DE USUARIOS (Uno de cada rol)
        estudiante = models.Usuario(
            rut="12.345.678-9",
            correo_institucional="alumno@universidad.cl",
            password_hash="clave123",
            rol=models.RolUsuario.estudiante
        )
        tutor = models.Usuario(
            rut="15.678.901-2",
            correo_institucional="tutor@hospital.cl",
            password_hash="tutor123",
            rol=models.RolUsuario.tutor
        )
        coordinador = models.Usuario(
            rut="9.876.543-2",
            correo_institucional="coord@universidad.cl",
            password_hash="coord123",
            rol=models.RolUsuario.coordinador
        )
        db.add_all([estudiante, tutor, coordinador])
        db.commit() # Commit para que SQLAlchemy les asigne sus IDs correlativos (1, 2, 3)

        # 3. CREACIÓN DE CENTROS CLÍNICOS (Campos de práctica con geocercas)
        hospital_fricke = models.CentroClinico(
            nombre="Hospital Dr. Gustavo Fricke",
            latitud=-33.0245,
            longitud=-71.5518,
            radio_permitido=200 # metros de tolerancia
        )
        cesfam_miraflores = models.CentroClinico(
            nombre="CESFAM Miraflores",
            latitud=-33.0135,
            longitud=-71.5361,
            radio_permitido=150
        )
        db.add_all([hospital_fricke, cesfam_miraflores])
        db.commit()

        # 4. CREACIÓN DE LA ASIGNACIÓN (Cruzamos al Alumno 1 con el Hospital 1)
        asignacion_activa = models.Asignacion(
            estudiante_id=estudiante.id,
            centro_id=hospital_fricke.id,
            fecha_inicio_rotativa=datetime(2026, 5, 1, 8, 0),
            fecha_fin_rotativa=datetime(2026, 7, 31, 20, 0)
        )
        db.add(asignacion_activa)
        db.commit()

        print("\n✅ ¡Base de datos reiniciada y poblada con éxito!")
        print("--------------------------------------------------")
        print("🔑 CREDENCIALES DE PRUEBA DISPONIBLES:")
        print(f"   • [Estudiante]  Email: {estudiante.correo_institucional} | Pass: clave123")
        print(f"   • [Tutor]       Email: {tutor.correo_institucional} | Pass: tutor123")
        print(f"   • [Coordinador] Email: {coordinador.correo_institucional} | Pass: coord123")
        print("\n📍 GEOCERCAS CONFIGURADAS:")
        print(f"   • ID {hospital_fricke.id}: {hospital_fricke.nombre} (Radio: {hospital_fricke.radio_permitido}m)")
        print(f"   • ID {cesfam_miraflores.id}: {cesfam_miraflores.nombre} (Radio: {cesfam_miraflores.radio_permitido}m)")
        print(f"\n📅 ASIGNACIÓN ACTIVA CREADA:")
        print(f"   • Estudiante ID {estudiante.id} asignado a Centro ID {hospital_fricke.id} (Asignación ID: 1)")
        print("--------------------------------------------------\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Error crítico durante la carga de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    limpiar_y_poblar()
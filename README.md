# 🚀 InternShifts - MVP Backend

API modular para la gestión de trazabilidad clínica, control de asistencia mediante geocercas geográficas y auditoría analítica de rotativas de salud.

---

## 1. Arquitectura de la Solución

El sistema está desarrollado sobre **Python 3.13** utilizando una arquitectura de alta cohesión basada en **FastAPI** y **SQLAlchemy** (ORM). La persistencia de datos utiliza un motor relacional **SQLite** local (`internshifts.db`).

### Estructura del Proyecto

* `database.py`: Conexión al motor SQLite y ciclo de vida de la sesión de BD.
* `models.py`: Modelos relacionales (Tablas) y Enums estrictos de negocio.
* `schemas.py`: Esquemas de validación y tipado de datos (Pydantic).
* `requirements.txt`: Registro exacto de dependencias fijadas para el entorno.
* `seed.py`: Script automatizado de limpieza, reseteo y carga masiva inicial.
* `main.py`: Punto de entrada de la API y políticas de seguridad CORS.
* `routers/`: Controladores modulares por dominio de negocio.
  * `usuarios.py`: Autenticación y perfiles de usuarios (RF-01).
  * `geocercas.py`: Administración de campos clínicos y perímetros (RF-07).
  * `asignaciones.py`: Configuración de rotativas académicas por alumno (RF-08).
  * `asistencia.py`: Motor geométrico de presencia (Haversine) y marcas (RF-02/RF-04).

---

## 2. Configuración e Instalación del Entorno Local

Para replicar de forma idéntica el entorno de desarrollo, ejecute la siguiente secuencia en su terminal:

```bash
# 1. Ingresar a la carpeta raíz del proyecto
cd InternShifts

# 2. Crear el entorno virtual aislado
python3 -m venv .venv

# 3. Activar el entorno virtual
source .venv/bin/activate

# 4. Instalar el árbol de dependencias exacto
pip install -r requirements.txt
```

---

## 3. Inicialización Automática de Datos (Seeding)

El proyecto cuenta con un script de carga inicial (`seed.py`) que destruye la base de datos anterior y la reconstruye con datos de prueba realistas para el equipo.

### Ejecución del Reseteo

Apague el servidor web (`Ctrl + C` en la terminal) y ejecute:

```bash
python seed.py
```

### Datos Sembrados Disponibles:

* **Ecosistema de Usuarios:**
  * **Estudiante:** `alumno@universidad.cl` | Contraseña: `clave123` *(ID: 1)*
  * **Tutor Clínico:** `tutor@hospital.cl` | Contraseña: `tutor123` *(ID: 2)*
  * **Coordinador:** `coord@universidad.cl` | Contraseña: `coord123` *(ID: 3)*

* **Geocercas de Campos Clínicos:**
  * **Hospital Dr. Gustavo Fricke:** Lat: `-33.0245`, Lon: `-71.5518` | Radio: `200m` *(ID: 1)*
  * **CESFAM Miraflores:** Lat: `-33.0135`, Lon: `-71.5361` | Radio: `150m` *(ID: 2)*

* **Asignaciones Activas:** El Estudiante ID 1 está vinculado contractualmente para rotar en el Hospital ID 1 *(Asignación ID: 1)*.

---

## 4. Protocolo de Pruebas Manuales (Swagger UI)

Una vez poblada la base de datos, encienda el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

Abra el navegador web e ingrese a: **`http://127.0.0.1:8000/docs`**

### Secuencia de Testeo Completa:

1. **Autenticación (RF-01):** Pruebe el endpoint `POST /usuarios/login` enviando el correo del alumno y su contraseña. Debe retornar un código **200 OK**.
2. **Marcaje de Entrada (RF-02):** Pruebe `POST /asistencia/entrada` con la `asignacion_id: 1` y las coordenadas exactas del Hospital Fricke. Retornará **201 Created** si está dentro del radio.
3. **Bloqueo Antifraude:** Intente marcar en el mismo endpoint alterando las coordenadas para alejarse más de 200 metros. La API responderá con un **403 Forbidden** bloqueando el fraude geográfico.
4. **Cierre de Turno con Justificación (RF-04):** Use `POST /asistencia/salida` enviando el `registro_id: 1` y una justificación en texto libre. El sistema calculará las horas brutas reales de permanencia.
5. **Reporte del Coordinador (RF-09):** Acceda a `GET /coordinador/reporte-csv`, ejecute y descargue el archivo `.csv`. Al abrirlo en Excel, verá toda la auditoría transaccional con las notas del alumno.

---

## 5. Políticas de Conectividad Frontend (CORS)

El archivo `main.py` incorpora un middleware global de control de acceso para permitir que el backend interactúe sin restricciones con interfaces externas de desarrollo (como emuladores móviles de Flutter, React Native o servidores locales vinculados a prototipos de Figma):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

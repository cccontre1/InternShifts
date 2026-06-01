Documentación Técnica y Guía de Pruebas: InternShifts (MVP Backend)
Este documento detalla la arquitectura, el proceso de instalación local y la suite de pruebas funcionales para validar el núcleo transaccional, geográfico y de auditoría del sistema InternShifts.

1. Arquitectura de la Solución
El backend está desarrollado sobre Python 3.13 utilizando una arquitectura modular de alta cohesión basada en FastAPI y SQLAlchemy (ORM). La persistencia de datos utiliza un motor relacional SQLite local (internshifts.db).

Estructura del Proyecto
Plaintext
￼
￼
InternShifts/
├── database.py       # Conexión al motor SQLite y ciclo de vida de la sesión de BD.
├── models.py         # Modelos relacionales (Tablas) y Enums estrictos de negocio.
├── schemas.py        # Esquemas de validación y tipado de datos entrantes/salientes (Pydantic).
├── requirements.txt  # Registro exacto de dependencias fijadas para el entorno.
├── seed.py           # Script automatizado de limpieza, reseteo y carga masiva inicial.
├── main.py           # Punto de entrada de la API y políticas de seguridad CORS.
└── routers/          # Controladores modulares por dominio de negocio.
    ├── __init__.py
    ├── usuarios.py   # Autenticación y perfiles de usuarios (RF-01).
    ├── geocercas.py  # Administración de campos clínicos y perímetros (RF-07).
    ├── asignaciones.py# Configuración de rotativas académicas por alumno (RF-08).
    └── asistencia.py # Motor geométrico de presencia (Haversine) y marcas (RF-02/RF-04).
2. Configuración e Instalación del Entorno Local
Para replicar de forma idéntica el entorno de desarrollo en un nuevo computador, ejecute la siguiente secuencia en su terminal:

Bash
￼
￼
# 1. Ingresar a la carpeta raíz del proyecto
cd InternShifts

# 2. Crear el entorno virtual aislado
python3 -m venv .venv

# 3. Activar el entorno virtual (según el Sistema Operativo)
source .venv/bin/activate  # En Linux / macOS
# .venv\Scripts\activate   # En Windows (CMD / PowerShell)

# 4. Instalar el árbol de dependencias exacto fijado para el MVP
pip install -r requirements.txt
3. Inicialización Automática de Datos (Seeding)
Para garantizar un entorno de pruebas controlado y libre de estados alterados, el proyecto cuenta con un script de carga inicial (seed.py). Este script destruye la base de datos anterior y la reconstruye en milisegundos con datos de prueba realistas.

Ejecución del Reseteo
Apague el servidor web (Ctrl + C en la terminal) y ejecute:

Bash
￼
￼
python seed.py
Datos Sembrados Disponibles:
Ecosistema de Usuarios:

Estudiante: alumno@universidad.cl | Contraseña: clave123 (ID Asignado: 1)

Tutor Clínico: tutor@hospital.cl | Contraseña: tutor123 (ID Asignado: 2)

Coordinador: coord@universidad.cl | Contraseña: coord123 (ID Asignado: 3)

Geocercas de Campos Clínicos:

Hospital Dr. Gustavo Fricke: Lat: -33.0245, Lon: -71.5518 | Radio permitido: 200m (ID: 1)

CESFAM Miraflores: Lat: -33.0135, Lon: -71.5361 | Radio permitido: 150m (ID: 2)

Asignaciones (Rotativas Activas):

El Estudiante ID 1 está vinculado contractualmente para rotar en el Hospital ID 1 (Asignación ID: 1).

4. Protocolo de Pruebas Manuales (Swagger UI)
Una vez poblada la base de datos, encienda el servidor de desarrollo:

Bash
￼
￼
uvicorn main:app --reload
Abra el navegador web e ingrese a la interfaz interactiva de pruebas: http://127.0.0.1:8000/docs

Ejecute los siguientes casos de prueba en orden cronológico para simular el flujo transaccional completo:

Caso de Prueba 1: Autenticación de Perfil (RF-01)
Despliegue el endpoint POST /usuarios/login.

Haga clic en "Try it out".

Reemplace el cuerpo de la petición (Request body) por las credenciales del alumno:

JSON
￼
￼
{
  "correo_institucional": "alumno@universidad.cl",
  "password": "clave123"
}
Presione "Execute".

Validación: El sistema debe retornar un código 200 OK junto con el objeto JSON del perfil del usuario, exponiendo su RUT y rol verificado.

Caso de Prueba 2: Marcaje de Entrada Exitoso (RF-02)
Despliegue el endpoint POST /asistencia/entrada.

Haga clic en "Try it out".

Simule que el celular del alumno envía coordenadas válidas dentro del Hospital Fricke:

JSON
￼
￼
{
  "asignacion_id": 1,
  "latitud_actual": -33.0245,
  "longitud_actual": -71.5518
}
Presione "Execute".

Validación: El backend procesa las coordenadas mediante la fórmula matemática de Haversine:

d=2rarcsin( 
sin 
2
 ( 
2
Δϕ
​
 )+cos(ϕ 
1
​
 )cos(ϕ 
2
​
 )sin 
2
 ( 
2
Δλ
​
 )
￼
​
 )
Al verificar que la distancia es menor al radio permitido, retorna un código 201 Created, almacena la marca de tiempo exacta del servidor y genera un registro_id: 1 en estado pendiente.

Caso de Prueba 3: Bloqueo Antifraude por Disparidad Geográfica
En la misma ruta POST /asistencia/entrada, simule un intento de marcaje remoto (por ejemplo, alterando levemente la latitud para ubicarse fuera del hospital):

JSON
￼
￼
{
  "asignacion_id": 1,
  "latitud_actual": -33.0200,
  "longitud_actual": -71.5518
}
Presione "Execute".

Validación: El motor geométrico detecta que la distancia excede el límite del centro clínico. La API frena la operación y responde con un código 403 Forbidden, detallando los metros de desfase y denegando la marca en la base de datos.

Caso de Prueba 4: Cierre de Turno y Justificación (RF-02)
Despliegue el endpoint POST /asistencia/salida.

Haga clic en "Try it out".

Ingrese los datos de salida obligatorios junto con una nota aclaratoria en texto libre:

JSON
￼
￼
{
  "registro_id": 1,
  "latitud_actual": -33.0245,
  "longitud_actual": -71.5518,
  "justificacion": "Retiro anticipado de la jornada debido a suspensión de cirugías programadas por contingencia interna."
}
Presione "Execute".

Validación: El sistema evalúa el GPS de salida (aplicando bloqueo antifraude si está fuera del recinto). Si es correcto, estampa la hora de salida, calcula de manera transparente la fracción de horas totales trabajadas y almacena la justificación humana. Retorna código 200 OK.

Caso de Prueba 5: Extracción de Auditoría para Coordinación (RF-09)
Suba hasta la sección Panel del Coordinador (Reportes).

Despliegue el endpoint GET /coordinador/reporte-csv.

Haga clic en "Try it out" y luego en "Execute".

En el bloque de respuesta inferior, haga clic en el enlace azul "Download file".

Validación: El sistema exportará un archivo estructurado .csv delimitado por punto y coma (;), exponiendo de manera limpia los RUTs, nombres de hospitales, marcas de tiempo, horas brutas y las justificaciones ingresadas por el alumno, listo para auditorías institucionales o procesamiento analítico.

5. Políticas de Conectividad Frontend (CORS)
Para que el backend interactúe sin restricciones con interfaces externas de desarrollo (como emuladores móviles de Flutter, React Native o servidores locales de pruebas vinculados a tus prototipos de Figma), el archivo main.py incorpora un middleware global de control de acceso:

Python
￼
￼
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite solicitudes de cualquier origen en fase MVP
    allow_credentials=True,
    allow_methods=["*"], # Habilita métodos GET, POST, PATCH, OPTIONS, etc.
    allow_headers=["*"], # Permite inyección de cabeceras de seguridad personalizadas
)
(Nota: Para la fase de despliegue en producción, el parámetro allow_origins se restringirá exclusivamente a los dominios oficiales de la aplicación).
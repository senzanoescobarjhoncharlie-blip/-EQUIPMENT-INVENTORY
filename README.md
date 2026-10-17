# PROYECTO: SISTEMA DE INVENTARIO DE EQUIPOS INFORMÁTICOS 💻🔧

API REST desarrollada con **FastAPI** y **MongoDB Atlas** mediante **PyMongo** para la administración integral de equipos informáticos institucionales. Permite registrar características técnicas, ubicación física, responsable asignado y el historial cronológico de mantenimientos preventivos y correctivos, aplicando validaciones estrictas con **Pydantic v2**.

---

## 📋 Tabla de Contenidos
1. [Características Principales](#-características-principales)
2. [Estructura del Documento en MongoDB](#-estructura-del-documento-en-mongodb)
3. [Estructura del Proyecto](#-estructura-del-proyecto)
4. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
5. [Instalación y Ejecución Local](#-instalación-y-ejecución-local)
6. [Variables de Entorno](#-variables-de-entorno)
7. [Documentación de la API y Endpoints](#-documentación-de-la-api-y-endpoints)
8. [Pruebas Automatizadas con Pytest](#-pruebas-automatizadas-con-pytest)
9. [Flujo de Trabajo Git y GitHub](#-flujo-de-trabajo-git-y-github)
10. [Reglas de Protección en GitHub (Rulesets)](#-reglas-de-protección-en-github-rulesets)
11. [Integración Continua (GitHub Actions)](#-integración-continua-github-actions)
12. [Despliegue en Vercel](#-despliegue-en-vercel)

---

## 🚀 Características Principales

- **Las diez (10) funcionalidades obligatorias implementadas y verificadas**:
  1. **Registrar equipo**: `POST /api/v1/equipos` con validación de duplicados (código y serie).
  2. **Listar todos los equipos**: `GET /api/v1/equipos` con paginación (`skip`, `limit`) y filtros.
  3. **Consultar equipo por identificador**: `GET /api/v1/equipos/{equipo_id}` con validación de ObjectId (400 si es inválido, 404 si no existe).
  4. **Modificar equipo**: `PATCH /api/v1/equipos/{equipo_id}` con actualización parcial y validación de colisiones (409).
  5. **Eliminar equipo**: `DELETE /api/v1/equipos/{equipo_id}` retornando `204 No Content` sin cuerpo de respuesta.
  6. **Buscar por código, serie o modelo**: `GET /api/v1/equipos/buscar` con soporte para parámetros `q`, `codigo`, `numero_serie` o `modelo`.
  7. **Filtrar por tipo**: `GET /api/v1/equipos/filtrar/tipo` (o vía path `/tipo/{tipo}`).
  8. **Filtrar por marca**: `GET /api/v1/equipos/filtrar/marca` (o vía path `/marca/{marca}`).
  9. **Filtrar por estado**: `GET /api/v1/equipos/filtrar/estado` (o vía path `/estado/{estado}`).
  10. **Consultar historial de mantenimiento**: `GET /api/v1/equipos/{equipo_id}/mantenimientos` (devuelve lista vacía `[]` si no hay registros o 404 si el equipo no existe).
  - *Funcionalidad de soporte*: `POST /api/v1/equipos/{equipo_id}/mantenimientos` para registrar mantenimientos técnicos.
- **Colección única en MongoDB**: Toda la información reside en una única colección llamada `equipos`.
- **Validaciones de negocio**:
  - Campos no vacíos ni con solo espacios en blanco.
  - Normalización de estados (`disponible`, `asignado`, `en_mantenimiento`, `dado_de_baja`, `operativo`).
  - Validación de fechas ISO (`YYYY-MM-DD`).
- **Swagger UI y OpenAPI**: Documentación interactiva en `/docs` y `/redoc`.
- **Health Check**: Endpoint `/health` para monitorizar el estado y la conexión con MongoDB Atlas.

---

## 📄 Estructura del Documento en MongoDB

Cada documento de la colección `equipos` almacena la entidad completa sin colecciones adicionales:

```json
{
  "_id": "6614a93f412d2b588390b3e1",
  "codigo": "EQ-LAP-001",
  "tipo": "Laptop",
  "marca": "Dell",
  "modelo": "Latitude 5420",
  "numero_serie": "SN-DL5420-9988",
  "fecha_adquisicion": "2024-02-15",
  "estado": "disponible",
  "caracteristicas": [
    "Intel Core i7 11th Gen",
    "16 GB RAM DDR4",
    "SSD 512GB NVMe"
  ],
  "ubicacion": {
    "edificio": "Edificio Central",
    "ambiente": "Laboratorio de Cómputo 3",
    "responsable": "Ing. Carlos Mendoza"
  },
  "mantenimientos": [
    {
      "id": "mant-001",
      "fecha": "2025-01-10",
      "tipo": "Preventivo",
      "descripcion": "Limpieza general interna y cambio de pasta térmica",
      "tecnico": "Téc. Roberto Gómez",
      "costo": 35.0
    }
  ]
}
```

---

## 📂 Estructura del Proyecto

```text
inventario-equipos-api/
├── .github/
│   └── workflows/
│       └── ci.yml               # Workflow de integración continua (Python 3.10 y 3.12.3)
├── api/
│   ├── __init__.py
│   ├── index.py                 # Punto de entrada para Serverless en Vercel
│   └── v1/
│       ├── __init__.py
│       ├── router.py            # Enrutador principal v1
│       └── endpoints/
│           ├── __init__.py
│           └── equipos.py       # Controladores de las 10 funcionalidades
├── core/
│   ├── __init__.py
│   ├── config.py                # Configuración Pydantic Settings
│   └── database.py              # Conexión PyMongo con ciclo de vida (lifespan)
├── schemas/
│   ├── __init__.py
│   ├── equipo.py                # Esquemas y validadores Pydantic v2
│   ├── mantenimiento.py         # Modelos anidados de mantenimientos
│   └── ubicacion.py             # Modelos anidados de ubicación física
├── utils/
│   ├── __init__.py
│   ├── mongo.py                 # Validación de ObjectId y serialización JSON
│   ├── errors.py                # Excepciones HTTP tipadas
│   └── serializers.py           # Serializadores de colecciones y documentos
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures aisladas con mongomock y TestClient
│   └── test_equipos.py          # 19 pruebas de integración y casos borde
├── .env                         # Variables de entorno locales (ignorado por Git)
├── .env.example                 # Plantilla pública de variables
├── .gitignore                   # Exclusiones de Git (sin secretos)
├── main.py                      # Instancia principal FastAPI
├── requirements.txt             # Dependencias del proyecto
├── vercel.json                  # Configuración de despliegue en Vercel
└── README.md                    # Documentación técnica
```

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.10+ / 3.12 / 3.14
- **Framework Web**: FastAPI (v0.112+)
- **Servidor ASGI**: Uvicorn
- **Base de Datos**: MongoDB Atlas vía PyMongo (v4.6+)
- **Validación de Datos**: Pydantic v2 y pydantic-settings
- **Pruebas Automatizadas**: Pytest, HTTPX y MongoMock
- **Control de Versiones**: Git y GitHub
- **Integración Continua**: GitHub Actions (Ubuntu, Python 3.10 y 3.12.3)
- **Plataforma de Despliegue**: Vercel

---

## ⚙️ Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/senzanoescobarjhoncharlie-blip/-EQUIPMENT-INVENTORY.git
cd -EQUIPMENT-INVENTORY
```

### 2. Crear y activar el entorno virtual
En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
En Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea tu archivo `.env` a partir de `.env.example`:
```bash
cp .env.example .env
```
Configura tu cadena de conexión real de **MongoDB Atlas**:
```ini
APP_NAME="Sistema de Inventario de Equipos Informaticos"
APP_VERSION="1.0.0"
API_V1_PREFIX="/api/v1"

MONGODB_URI="mongodb+srv://<usuario>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
MONGODB_DB="inventario_equipos_db"
MONGODB_COLLECTION="equipos"
```

### 5. Iniciar la aplicación
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- **Documentación Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Pruebas Automatizadas con Pytest

Las pruebas están completamente aisladas mediante `mongomock`, por lo que **no requieren credenciales de MongoDB en producción ni modifican datos reales**.

Ejecución de la suite completa:
```bash
pytest -v tests/
```
Cobertura de casos de prueba:
- Registro válido e inválido (campos vacíos o con solo espacios).
- Conflictos de duplicidad (409) en código o serie.
- Listado general y paginación con `skip` y `limit`.
- Consulta por ID válido, inexistente (404) e ID con formato inválido (400).
- Modificación parcial (`PATCH`) y validación de colisiones.
- Eliminación exitosa (`204 No Content` sin cuerpo).
- Búsqueda flexible por código, número de serie o modelo.
- Filtros por categoría de tipo, marca y estado actual.
- Historial de mantenimiento vacío (`[]`), con registros y equipo inexistente.
- Verificación de arranque y `/health`.

---

## 📌 Documentación de Endpoints

Prefijo general: `/api/v1`

| # | Método | Ruta | Código Éxito | Descripción |
|---|--------|------|--------------|-------------|
| 1 | `POST` | `/api/v1/equipos` | `201 Created` | Registra un nuevo equipo con validación de unicidad. |
| 2 | `GET` | `/api/v1/equipos` | `200 OK` | Lista equipos con paginación (`skip`, `limit`) y filtros. |
| 3 | `GET` | `/api/v1/equipos/{equipo_id}` | `200 OK` | Consulta el detalle de un equipo por su `ObjectId`. |
| 4 | `PATCH` | `/api/v1/equipos/{equipo_id}` | `200 OK` | Modificación parcial de campos permitidos. |
| 5 | `DELETE` | `/api/v1/equipos/{equipo_id}` | `204 No Content` | Eliminación permanente del equipo (sin cuerpo). |
| 6 | `GET` | `/api/v1/equipos/buscar` | `200 OK` | Búsqueda por parámetros `q`, `codigo`, `numero_serie` o `modelo`. |
| 7 | `GET` | `/api/v1/equipos/filtrar/tipo` | `200 OK` | Filtra equipos por tipo/categoría. |
| 8 | `GET` | `/api/v1/equipos/filtrar/marca` | `200 OK` | Filtra equipos por marca del fabricante. |
| 9 | `GET` | `/api/v1/equipos/filtrar/estado` | `200 OK` | Filtra equipos por estado (`disponible`, `asignado`, etc.). |
| 10 | `GET` | `/api/v1/equipos/{equipo_id}/mantenimientos` | `200 OK` | Devuelve el historial de mantenimientos. |
| - | `POST` | `/api/v1/equipos/{equipo_id}/mantenimientos` | `201 Created` | Agrega un nuevo registro de mantenimiento. |
| - | `GET` | `/health` | `200 OK` / `503` | Verifica el estado del servicio y conexión a MongoDB. |

---

## 🌿 Flujo de Trabajo Git y GitHub

El proyecto sigue una estrategia rigurosa de ramas protegidas:
1. `main`: Rama de producción estable.
2. `dev`: Rama de integración continua.
3. Ramas de funcionalidad `feat/...`:
   - Se crean desde `dev`.
   - Se implementa la funcionalidad y sus pruebas.
   - Se sube al repositorio y se abre Pull Request con destino `dev`.
   - Tras la aprobación y éxito de GitHub Actions, se realiza el merge en `dev`.
4. Pull Request final: `dev` → `main` para el despliegue a producción.

---

## 🛡️ Reglas de Protección en GitHub (Rulesets)

Para proteger la integridad de las ramas `main` y `dev`, configura en el repositorio de GitHub:

### Pasos de configuración:
1. Dirígete a **Settings** → **Rules** → **Rulesets** → **New ruleset** → **New branch ruleset**.
2. **Ruleset para `main`**:
   - **Name**: `Protección Main (Producción)`
   - **Enforcement status**: `Active`
   - **Target branches**: Incluir `main`
   - **Rules**:
     - ✅ **Restrict deletions** (Evitar eliminar la rama).
     - ✅ **Require a pull request before merging** (Exigir al menos 1 aprobación).
     - ✅ **Block force pushes** (Bloquear `git push --force`).
     - ✅ **Require status checks to pass**:
       - Seleccionar: `Build (Python 3.10)` y `Build (Python 3.12.3)`.
3. **Ruleset para `dev`**:
   - **Name**: `Protección Dev (Integración)`
   - **Enforcement status**: `Active`
   - **Target branches**: Incluir `dev`
   - **Rules**:
     - ✅ **Restrict deletions**
     - ✅ **Require a pull request before merging**
     - ✅ **Block force pushes**
     - ✅ **Require status checks to pass**:
       - Seleccionar: `Build (Python 3.10)` y `Build (Python 3.12.3)`.

---

## 🚀 Integración Continua (GitHub Actions)

El archivo `.github/workflows/ci.yml` se ejecuta automáticamente en cada Push y Pull Request hacia `main` o `dev`.

### Matriz de pruebas:
- **Python 3.10**
- **Python 3.12.3**

### Pasos ejecutados:
1. Checkout del código con `actions/checkout@v4`.
2. Configuración de Python y caché de pip con `actions/setup-python@v5`.
3. Instalación de `requirements.txt`.
4. Verificación de compilación de sintaxis con `python -m compileall`.
5. Comprobación de arranque de la aplicación y registro de rutas de FastAPI.
6. Ejecución de la suite de pruebas automatizadas con `pytest -v tests/`.

---

## ☁️ Despliegue en Vercel

La aplicación está preparada para despliegue serverless en **Vercel** mediante `vercel.json` y `api/index.py`.

### Variables a configurar en el panel de Vercel:
En **Project Settings** → **Environment Variables**:
- `MONGODB_URI`: Tu cadena de conexión completa de MongoDB Atlas (ejemplo: `mongodb+srv://...`).
- `MONGODB_DB`: Nombre de la base de datos (ejemplo: `inventario_equipos_db`).
- `MONGODB_COLLECTION`: Nombre de la colección (`equipos`).
- `APP_NAME`: `Sistema de Inventario de Equipos Informaticos`
- `APP_VERSION`: `1.0.0`
- `API_V1_PREFIX`: `/api/v1`

### Pasos para desplegar:
1. Conecta tu repositorio de GitHub en Vercel.
2. Selecciona la rama de producción (`main`).
3. Agrega las variables de entorno mencionadas.
4. Presiona **Deploy**.
5. Accede a tu URL asignada: `https://<tu-proyecto>.vercel.app/docs`.

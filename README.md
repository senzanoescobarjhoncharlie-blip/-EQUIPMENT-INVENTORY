# PROYECTO 11: SISTEMA DE INVENTARIO DE EQUIPOS INFORMÁTICOS 💻🔧

API REST desarrollada con **FastAPI** y **MongoDB Atlas** para la administración integral de equipos informáticos institucionales, gestionando características técnicas, ubicaciones físicas, responsables y el historial cronológico de mantenimientos.

[![CI Pipeline](https://github.com/senzanoescobarjhoncharlie-blip/-EQUIPMENT-INVENTORY/actions/workflows/ci.yml/badge.svg)](https://github.com/senzanoescobarjhoncharlie-blip/-EQUIPMENT-INVENTORY/actions)
[![Vercel Deployment](https://img.shields.io/badge/Vercel-Deployed-success?logo=vercel&style=flat)](https://equipment-inventory-liard.vercel.app)
[![Swagger Docs](https://img.shields.io/badge/API_Docs-Swagger_UI-blue?logo=swagger&style=flat)](https://equipment-inventory-liard.vercel.app/docs)

🌐 **URL de Producción en Vivo**: [https://equipment-inventory-liard.vercel.app](https://equipment-inventory-liard.vercel.app)  
📖 **Documentación Interactiva (Swagger)**: [https://equipment-inventory-liard.vercel.app/docs](https://equipment-inventory-liard.vercel.app/docs)  
🩺 **Estado de Salud de la API y MongoDB**: [https://equipment-inventory-liard.vercel.app/health](https://equipment-inventory-liard.vercel.app/health)  

---

## 📋 Tabla de Contenidos
1. [Características Principales](#-características-principales)
2. [Estructura del Documento en MongoDB](#-estructura-del-documento-en-mongodb)
3. [Estructura del Proyecto](#-estructura-del-proyecto)
4. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
5. [Instalación y Ejecución Local](#-instalación-y-ejecución-local)
6. [Variables de Entorno](#-variables-de-entorno)
7. [Documentación de la API y Endpoints](#-documentación-de-la-api-y-endpoints)
8. [Flujo de Trabajo Git y GitHub](#-flujo-de-trabajo-git-y-github)
9. [Integración Continua (GitHub Actions)](#-integración-continua-github-actions)
10. [Despliegue en Vercel](#-despliegue-en-vercel)

---

## 🚀 Características Principales
- **10 Funcionalidades requeridas implementadas y validadas**:
  1. Registrar un nuevo equipo con validación de duplicados en código y número de serie.
  2. Listar todos los equipos con soporte para paginación (`skip`, `limit`) y filtros combinables.
  3. Consultar equipo por identificador (`_id` de MongoDB).
  4. Modificar información de un equipo (parcial o total).
  5. Eliminar un equipo mediante su identificador.
  6. Búsqueda flexible por código, número de serie o modelo (insensible a mayúsculas).
  7. Filtrado de equipos por tipo (Laptop, Desktop, Servidor, Impresora, etc.).
  8. Filtrado de equipos por marca (Dell, HP, Lenovo, Cisco, etc.).
  9. Filtrado de equipos por estado (Operativo, En Mantenimiento, De Baja, etc.).
  10. Consulta del historial de mantenimientos de un equipo.
  - *Extra*: Registro de un nuevo mantenimiento preventivo o correctivo directamente sobre un equipo.
- **Una sola colección en la base de datos (`equipos`)** con objetos embebidos (`ubicacion`) y arreglos de documentos (`mantenimientos` y `caracteristicas`).
- Documentación interactiva automática con **Swagger UI** y **ReDoc**.
- Verificación de estado del servicio y conexión a base de datos (`/health`).

---

## 📄 Estructura del Documento en MongoDB

Cada documento de la colección `equipos` cumple con la siguiente estructura requerida:

```json
{
  "_id": "6614a93f412d2b588390b3e1",
  "codigo": "EQ-LAP-001",
  "tipo": "Laptop",
  "marca": "Dell",
  "modelo": "Latitude 5420",
  "numero_serie": "SN-DL5420-9988",
  "fecha_adquisicion": "2024-02-15",
  "estado": "Operativo",
  "caracteristicas": [
    "Intel Core i7 11th Gen",
    "16 GB RAM DDR4",
    "SSD 512GB NVMe",
    "Pantalla 14 FHD"
  ],
  "ubicacion": {
    "edificio": "Edificio Central",
    "ambiente": "Laboratorio de Computo 3",
    "responsable": "Ing. Carlos Mendoza"
  },
  "mantenimientos": [
    {
      "id": "mant-001",
      "fecha": "2025-01-10",
      "tipo": "Preventivo",
      "descripcion": "Limpieza general interna y cambio de pasta termica",
      "tecnico": "Tec. Roberto Gomez",
      "costo": 35.0
    }
  ]
}
```

---

## 📂 Estructura del Proyecto

El proyecto sigue una arquitectura modular y escalable respetando los requerimientos de compilación del CI:

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml               # Workflow de CI para pull requests y push en main/dev
├── api/
│   ├── __init__.py
│   ├── index.py                 # Entrada para Vercel Serverless Function
│   └── v1/
│       ├── __init__.py
│       ├── router.py            # Enrutador principal v1
│       └── endpoints/
│           ├── __init__.py
│           └── equipos.py       # Controladores y rutas de equipos
├── core/
│   ├── __init__.py
│   ├── config.py                # Configuración y variables de entorno (Pydantic Settings)
│   └── database.py              # Conexión a MongoDB con PyMongo (cliente lazy)
├── schemas/
│   ├── __init__.py
│   ├── ubicacion.py             # Esquemas Pydantic para ubicación
│   ├── mantenimiento.py         # Esquemas Pydantic para mantenimientos
│   └── equipo.py                # Esquemas Pydantic para equipos (CRUD, filtros)
├── utils/
│   ├── __init__.py
│   ├── errors.py                # Validaciones de ObjectId y excepciones HTTP
│   └── serializers.py           # Serialización de ObjectId y fechas a JSON
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore                   # Exclusión de archivos sensibles, venv y temporales
├── main.py                      # Punto de entrada de la aplicación FastAPI
├── requirements.txt             # Dependencias del proyecto
├── vercel.json                  # Configuración para despliegue en Vercel
└── README.md                    # Documentación del proyecto
```

---

## 🛠️ Tecnologías Utilizadas

- **[Python 3.10+]**
- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web moderno, asíncrono y de alto rendimiento.
- **[Uvicorn](https://www.uvicorn.org/)**: Servidor ASGI ultrarrápido.
- **[PyMongo](https://pymongo.readthedocs.io/)**: Driver oficial de MongoDB para Python.
- **[Pydantic v2](https://docs.pydantic.dev/)**: Validación de datos y parseo mediante tipado en Python.
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)**: Gestión de configuración mediante variables de entorno.
- **[GitHub Actions](https://github.com/features/actions)**: Integración continua automatizada.
- **[Vercel](https://vercel.com/)**: Plataforma serverless para despliegue en la nube.

---

## ⚙️ Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/SISTEMA-DE-INVENTARIO-DE-EQUIPOS-INFORMATICOS.git
cd "SISTEMA-DE-INVENTARIO-DE-EQUIPOS-INFORMATICOS"
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
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copia el archivo `.env.example` como `.env`:
```bash
cp .env.example .env
```
Ajusta la variable `MONGODB_URI` con tu instancia local de MongoDB (`mongodb://localhost:27017`) o la URL de conexión de **MongoDB Atlas**.

### 5. Iniciar el servidor
```bash
uvicorn main:app --reload --port 8000
```
La aplicación estará disponible en:
- API Base: `http://localhost:8000`
- Documentación Interactiva (Swagger): `http://localhost:8000/docs`
- Documentación Alternativa (ReDoc): `http://localhost:8000/redoc`
- Chequeo de Salud: `http://localhost:8000/health`

---

## 🔐 Variables de Entorno

El archivo `.env` permite configurar los parámetros de ejecución:

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `APP_NAME` | Nombre de la aplicación en Swagger | `Sistema de Inventario de Equipos Informaticos` |
| `APP_VERSION` | Versión actual de la API | `1.0.0` |
| `API_V1_PREFIX` | Prefijo de rutas para la versión 1 | `/api/v1` |
| `MONGODB_URI` | Cadena de conexión hacia MongoDB | `mongodb://localhost:27017` |
| `MONGODB_DB` | Nombre de la base de datos | `inventario_equipos_db` |
| `MONGODB_COLLECTION` | Nombre de la colección de equipos | `equipos` |

> ⚠️ **Importante**: El archivo `.env` nunca debe subirse al repositorio. Está protegido por el archivo `.gitignore`.

---

## 📡 Documentación de la API y Endpoints

### 1. Registrar un nuevo equipo
- **Método**: `POST`
- **Ruta**: `/api/v1/equipos`
- **Código de Respuesta**: `201 Created`
- **Cuerpo de la Petición (Request Body)**:
```json
{
  "codigo": "EQ-LAP-001",
  "tipo": "Laptop",
  "marca": "Dell",
  "modelo": "Latitude 5420",
  "numero_serie": "SN-DL5420-9988",
  "fecha_adquisicion": "2024-02-15",
  "estado": "Operativo",
  "caracteristicas": [
    "Intel Core i7 11th Gen",
    "16 GB RAM DDR4",
    "SSD 512GB NVMe",
    "Pantalla 14 FHD"
  ],
  "ubicacion": {
    "edificio": "Edificio Central",
    "ambiente": "Laboratorio de Computo 3",
    "responsable": "Ing. Carlos Mendoza"
  },
  "mantenimientos": []
}
```

---

### 2. Listar todos los equipos
- **Método**: `GET`
- **Ruta**: `/api/v1/equipos`
- **Parámetros Opcionales de Consulta**:
  - `skip` (int, default: 0)
  - `limit` (int, default: 100)
  - `tipo` (str, opcional)
  - `marca` (str, opcional)
  - `estado` (str, opcional)
- **Ejemplo**: `GET /api/v1/equipos?skip=0&limit=10`

---

### 3. Consultar un equipo mediante su identificador
- **Método**: `GET`
- **Ruta**: `/api/v1/equipos/{id}`
- **Ejemplo**: `GET /api/v1/equipos/6614a93f412d2b588390b3e1`
- **Respuesta**: Devuelve el documento completo del equipo o `404 Not Found` si no existe.

---

### 4. Modificar la información de un equipo
- **Método**: `PUT`
- **Ruta**: `/api/v1/equipos/{id}`
- **Cuerpo de la Petición**: Admite actualización de cualquier campo o de la ubicación física:
```json
{
  "estado": "En Mantenimiento",
  "ubicacion": {
    "ambiente": "Taller de Soporte Tecnico",
    "responsable": "Lic. Ana Gutierrez"
  }
}
```

---

### 5. Eliminar un equipo
- **Método**: `DELETE`
- **Ruta**: `/api/v1/equipos/{id}`
- **Respuesta**:
```json
{
  "mensaje": "Equipo con identificador '6614a93f412d2b588390b3e1' eliminado exitosamente.",
  "id": "6614a93f412d2b588390b3e1",
  "eliminado": true
}
```

---

### 6. Buscar equipos por código, número de serie o modelo
- **Método**: `GET`
- **Ruta**: `/api/v1/equipos/buscar?q={termino}`
- **Ejemplo**: `GET /api/v1/equipos/buscar?q=Latitude`
- Realiza una búsqueda mediante `$regex` insensible a mayúsculas sobre los campos `codigo`, `numero_serie` y `modelo`.

---

### 7. Filtrar equipos por tipo
- **Método**: `GET`
- **Ruta**: `/api/v1/equipos/tipo/{tipo}` (o `/api/v1/equipos/filtrar/tipo/{tipo}`)
- **Ejemplo**: `GET /api/v1/equipos/tipo/Laptop`

---

### 8. Filtrar equipos por marca
- **Método**: `GET`
- **Ruta**: `/api/v1/equipos/marca/{marca}` (o `/api/v1/equipos/filtrar/marca/{marca}`)
- **Ejemplo**: `GET /api/v1/equipos/marca/Dell`

---

### 9. Filtrar equipos por estado
- **Método**: `GET`
- **Ruta**: `/api/v1/equipos/estado/{estado}` (o `/api/v1/equipos/filtrar/estado/{estado}`)
- **Ejemplo**: `GET /api/v1/equipos/estado/Operativo`

---

### 10. Consultar el historial de mantenimiento de un equipo
- **Método**: `GET`
- **Ruta**: `/api/v1/equipos/{id}/mantenimientos`
- **Respuesta**: Lista de mantenimientos registrados para dicho equipo.

---

### Extra: Registrar mantenimiento a un equipo
- **Método**: `POST`
- **Ruta**: `/api/v1/equipos/{id}/mantenimientos`
- **Cuerpo de la Petición**:
```json
{
  "fecha": "2025-03-15",
  "tipo": "Correctivo",
  "descripcion": "Reemplazo de teclado danado y formateo del sistema",
  "tecnico": "Ing. Marcos Flores",
  "costo": 45.00
}
```

---

## 🌿 Flujo de Trabajo Git y GitHub

Para cumplir con las buenas prácticas de ingeniería de software evaluadas en clase:

1. **Ramas Principales**:
   - `main`: Rama de producción. Contiene código listo para despliegue.
   - `dev`: Rama de integración continua y desarrollo.

2. **Creación de ramas de características (Feature branches)**:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/crud-equipos
   ```

3. **Commits semánticos**:
   ```bash
   git add .
   git commit -m "feat: implementar endpoints de busqueda y filtros de equipos"
   ```

4. **Pull Requests (PR)**:
   - Crear el Pull Request desde `feature/...` hacia `dev`.
   - Una vez comprobado el paso del CI en GitHub Actions, integrar a `dev`.
   - Realizar el PR final desde `dev` hacia `main`.

---

## 🧪 Integración Continua (GitHub Actions)

El workflow está configurado en `.github/workflows/ci.yml` y se activa automáticamente ante:
- Pushes directos a `main` y `dev`.
- Pull Requests cuyo destino sea `main` o `dev`.

### Pasos ejecutados por el CI:
1. **Checkout del código** con `actions/checkout@v4`.
2. **Matriz de versiones de Python**: se valida en `Python 3.10` y `Python 3.12.3`.
3. **Instalación de dependencias** y verificación de compatibilidad de paquetes.
4. **Compilación de código** con `compileall -q main.py api core schemas utils`.
5. **Verificación de arranque**: Importa `main.app` e inspecciona que todas las rutas se registren correctamente.

---

## ☁️ Despliegue en Vercel

### Requisitos previos:
1. Una cuenta activa en [Vercel](https://vercel.com/).
2. Un clúster gratuito en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).

### Pasos para desplegar:
1. **Subir el repositorio a GitHub**.
2. **Importar el proyecto en Vercel**:
   - En el panel de Vercel, haz clic en **"Add New"** > **"Project"**.
   - Selecciona el repositorio de GitHub.
3. **Configurar Variables de Entorno en Vercel**:
   - En la sección **Environment Variables**, añade:
     - `MONGODB_URI`: Tu cadena de conexión completa de MongoDB Atlas (ejemplo: `mongodb+srv://admin:password@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority`).
     - `MONGODB_DB`: `inventario_equipos_db`
     - `MONGODB_COLLECTION`: `equipos`
     - `APP_NAME`: `Sistema de Inventario de Equipos Informaticos`
     - `APP_VERSION`: `1.0.0`
     - `API_V1_PREFIX`: `/api/v1`
4. **Hacer clic en Deploy**:
   Vercel detectará la configuración de `vercel.json` y desplegará la API como función serverless.
5. Puedes acceder inmediatamente a `https://tu-proyecto.vercel.app/docs` para interactuar con la API en vivo.

# 🐾 GUÍA PASO A PASO - Sistema VetCare Pro en PyCharm

## 📋 ÍNDICE
1. [Crear el Proyecto en PyCharm](#1-crear-el-proyecto-en-pycharm)
2. [Configurar el Entorno Virtual](#2-configurar-el-entorno-virtual)
3. [Instalar Dependencias](#3-instalar-dependencias)
4. [Crear la Base de Datos en SQL Server](#4-crear-la-base-de-datos-en-sql-server)
5. [Estructura de Archivos](#5-estructura-de-archivos)
6. [Ejecutar la Aplicación](#6-ejecutar-la-aplicación)
7. [Solución de Problemas Comunes](#7-solución-de-problemas-comunes)

---

## 1. CREAR EL PROYECTO EN PYCHARM

### Paso 1.1: Abrir PyCharm
- Abre PyCharm
- Selecciona **"New Project"** (Nuevo Proyecto)

### Paso 1.2: Configurar el Nuevo Proyecto
- **Location (Ubicación):** `C:\Users\TuUsuario\PycharmProjects\VetCare_Pro`
- **Name (Nombre del proyecto):** `VetCare_Pro`
- **Python Interpreter:** Selecciona "New environment using Virtualenv"
  - Base interpreter: Python 3.10 o superior
- Click en **"Create"**

### Paso 1.3: Estructura de Carpetas a Crear
Una vez creado el proyecto, crea las siguientes carpetas:

```
VetCare_Pro/
│
├── app/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── controllers/
│   │   └── __init__.py
│   ├── templates/
│   │   ├── auth/
│   │   ├── propietarios/
│   │   ├── mascotas/
│   │   ├── veterinarios/
│   │   ├── consultas/
│   │   ├── tratamientos/
│   │   ├── vacunacion/
│   │   └── reportes/
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
│
├── database/
├── config.py
├── run.py
└── requirements.txt
```

**En PyCharm:**
1. Click derecho en la carpeta raíz del proyecto
2. Selecciona **New → Directory**
3. Crea cada carpeta según la estructura

---

## 2. CONFIGURAR EL ENTORNO VIRTUAL

### Paso 2.1: Verificar el Entorno Virtual
- Ve a **File → Settings → Project: VetCare_Pro → Python Interpreter**
- Verifica que muestre algo como: `Python 3.x (VetCare_Pro)`
- Si no está configurado, click en el engranaje ⚙️ y selecciona **"Add..."**

### Paso 2.2: Activar el Entorno Virtual (Terminal)
Abre el terminal integrado de PyCharm (View → Tool Windows → Terminal):

```bash
# Windows - El entorno virtual debería activarse automáticamente
# Si no, ejecuta:
.\venv\Scripts\activate
```

Deberías ver `(venv)` al inicio de la línea de comandos.

---

## 3. INSTALAR DEPENDENCIAS

### Paso 3.1: Crear requirements.txt
Crea el archivo `requirements.txt` en la raíz del proyecto con este contenido:

```
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-login==0.6.3
flask-wtf==1.2.1
sqlalchemy==2.0.23
pyodbc==5.0.1
werkzeug==3.0.1
python-dotenv==1.0.0
email-validator==2.1.0
wtforms==3.1.1
```

### Paso 3.2: Instalar las Dependencias
En el terminal de PyCharm:

```bash
pip install -r requirements.txt
```

### Paso 3.3: Verificar Instalación
```bash
pip list
```

Deberías ver todas las librerías instaladas.

---

## 4. CREAR LA BASE DE DATOS EN SQL SERVER

### Paso 4.1: Abrir SQL Server Management Studio (SSMS)
1. Abre SSMS
2. Conéctate a tu servidor (generalmente `localhost` o `.\SQLEXPRESS`)

### Paso 4.2: Ejecutar el Script de Creación
1. Click en **"New Query"** (Nueva Consulta)
2. Copia y pega el contenido del archivo `database/create_database.sql`
3. Click en **"Execute"** (F5)

### Paso 4.3: Verificar la Base de Datos
1. En el panel izquierdo, expande **Databases**
2. Deberías ver `VetCareDB`
3. Expande **Tables** para ver todas las tablas creadas

---

## 5. ESTRUCTURA DE ARCHIVOS

Los archivos del proyecto deben quedar así:

```
VetCare_Pro/
│
├── venv/                          # Entorno virtual (creado automáticamente)
│
├── app/
│   ├── __init__.py               # Inicialización de Flask
│   │
│   ├── models/
│   │   ├── __init__.py           # Exporta todos los modelos
│   │   ├── especie.py
│   │   ├── propietario.py
│   │   ├── mascota.py
│   │   ├── veterinario.py
│   │   ├── consulta.py
│   │   ├── tratamiento.py
│   │   ├── vacuna.py
│   │   ├── calendario_vacunacion.py
│   │   └── usuario.py
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── main_controller.py
│   │   ├── auth_controller.py
│   │   ├── propietario_controller.py
│   │   ├── mascota_controller.py
│   │   ├── veterinario_controller.py
│   │   ├── consulta_controller.py
│   │   ├── tratamiento_controller.py
│   │   ├── vacunacion_controller.py
│   │   └── reportes_controller.py
│   │
│   ├── templates/
│   │   ├── base.html             # Plantilla base
│   │   ├── index.html            # Página principal
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── propietarios/
│   │   │   ├── index.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── show.html
│   │   ├── mascotas/
│   │   │   ├── index.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── show.html
│   │   └── ... (demás carpetas)
│   │
│   └── static/
│       ├── css/
│       │   └── styles.css
│       ├── js/
│       │   └── main.js
│       └── img/
│           └── logo.png
│
├── database/
│   └── create_database.sql       # Script SQL
│
├── config.py                     # Configuración
├── run.py                        # Punto de entrada
└── requirements.txt              # Dependencias
```

---

## 6. EJECUTAR LA APLICACIÓN

### Paso 6.1: Configurar el Run Configuration en PyCharm

1. Click en **Run → Edit Configurations**
2. Click en el botón **"+"** y selecciona **"Python"**
3. Configura:
   - **Name:** `Run VetCare`
   - **Script path:** Selecciona `run.py`
   - **Working directory:** La carpeta raíz del proyecto
   - **Python interpreter:** El del entorno virtual
4. Click en **"Apply"** y luego **"OK"**

### Paso 6.2: Ejecutar
- Click en el botón verde ▶️ (Run)
- O presiona **Shift + F10**

### Paso 6.3: Abrir en el Navegador
Una vez ejecutándose, verás en la consola:
```
* Running on http://127.0.0.1:5000
```

Abre tu navegador y ve a: **http://localhost:5000**

---

## 7. SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "No module named 'pyodbc'"
```bash
pip install pyodbc
```

### Error: "ODBC Driver not found"
1. Descarga e instala: [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Reinicia PyCharm

### Error: "Login failed for user"
- Verifica que SQL Server esté ejecutándose
- En `config.py`, ajusta la cadena de conexión según tu configuración

### Error: "Cannot connect to SQL Server"
1. Abre **SQL Server Configuration Manager**
2. Verifica que **SQL Server (SQLEXPRESS)** esté ejecutándose
3. Habilita **TCP/IP** en Protocols for SQLEXPRESS

### El entorno virtual no se activa
```bash
# En PowerShell (como Administrador)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📝 NOTAS IMPORTANTES

1. **Nombre del Proyecto:** Usa `VetCare_Pro` (sin espacios, con guion bajo)
2. **Python:** Asegúrate de usar Python 3.10 o superior
3. **SQL Server:** Puede ser Express Edition (gratuito)
4. **ODBC Driver:** Necesitas el Driver 17 o 18 instalado

---

## 🚀 ¡LISTO!

Siguiendo estos pasos tendrás tu proyecto funcionando en PyCharm.

Si tienes problemas, revisa:
1. Que el entorno virtual esté activado
2. Que todas las dependencias estén instaladas
3. Que SQL Server esté corriendo
4. Que la base de datos esté creada

¡Éxito con tu proyecto! 🐾

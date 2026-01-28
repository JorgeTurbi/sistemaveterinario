# VetCare Pro - Sistema de Gestion Veterinaria

## Informacion Academica

**Proyecto Final de la Materia de Python**
**Master en Ciencia de Datos**
**Spain Business School (SBS)**

### Integrantes del Proyecto

- Ing. Jorge Turbi Lachapel
- Lic. Cesar Augusto Marchena Manon
- Lic. Robin Giron Ulloa Martinez
- Ing. Whilmis Pérez de Peña

---

## Descripcion del Proyecto

VetCare es un sistema integral de gestion para clinicas veterinarias desarrollado con Python y Flask. Permite administrar pacientes (mascotas), propietarios, consultas medicas, tratamientos, calendario de vacunacion y facturacion.

### Tecnologias Utilizadas

- **Backend:** Python 3.11+, Flask 3.0
- **Base de Datos:** Microsoft SQL Server 2019+
- **ORM:** SQLAlchemy 2.0
- **Autenticacion:** Flask-Login
- **Frontend:** HTML5, Bootstrap 5, Jinja2

---

## Estructura de la Base de Datos

### Diagrama de Entidades

El sistema utiliza una base de datos relacional normalizada en Tercera Forma Normal (3FN) con las siguientes entidades principales:

```
USUARIOS (1) -------- (0..1) VETERINARIOS
    |
    | registra
    v
CONSULTAS (N) ------- (1) MASCOTAS (N) ------- (1) PROPIETARIOS
    |                       |
    |                       |
    v                       v
TRATAMIENTOS           ESPECIES (1) ------- (N) VACUNAS
                            |
                            v
                    CALENDARIO_VACUNACION
                            |
                            v
                        FACTURAS
                            |
                            v
                    DETALLES_FACTURA ------- SERVICIOS
```

### Descripcion de Tablas

#### Tabla USUARIOS
Almacena los usuarios del sistema con control de acceso basado en roles.
- **Campos principales:** id_usuario, username, password_hash, nombre_completo, email, rol, activo
- **Roles disponibles:** Administrador, Veterinario, Recepcionista
- **Normalizacion:** 3FN - Todos los atributos dependen unicamente de la clave primaria

#### Tabla ESPECIES
Catalogo de especies animales atendidas.
- **Campos principales:** id_especie, nombre, descripcion, activo
- **Datos iniciales:** Perro, Gato, Ave, Conejo, Hamster, Pez, Tortuga, Otro

#### Tabla PROPIETARIOS
Informacion de los duenos de las mascotas (clientes).
- **Campos principales:** id_propietario, nombre, documento, telefono, email, direccion
- **Normalizacion:** 2FN - Eliminacion de dependencias parciales

#### Tabla VETERINARIOS
Profesionales medicos de la clinica.
- **Campos principales:** id_veterinario, nombre, colegiatura, especialidad, telefono, email
- **Relacion:** Vinculacion opcional 1:1 con usuarios del sistema

#### Tabla MASCOTAS
Pacientes de la clinica veterinaria.
- **Campos principales:** id_mascota, nombre, raza, fecha_nacimiento, sexo, peso, color
- **Relaciones:**
  - N:1 con PROPIETARIOS (cada mascota tiene un propietario)
  - N:1 con ESPECIES (cada mascota pertenece a una especie)

#### Tabla CONSULTAS
Registro de citas y atenciones medicas.
- **Campos principales:** id_consulta, fecha_hora, motivo, diagnostico, peso_actual, temperatura, estado, costo
- **Estados:** Programada, En Curso, Completada, Cancelada
- **Relaciones:**
  - N:1 con MASCOTAS
  - N:1 con VETERINARIOS
  - N:1 con USUARIOS (trazabilidad)

#### Tabla TRATAMIENTOS
Tratamientos prescritos en las consultas.
- **Campos principales:** id_tratamiento, descripcion, medicamento, dosis, duracion_dias, indicaciones
- **Estados:** Activo, Completado, Suspendido
- **Relacion:** N:1 con CONSULTAS

#### Tabla VACUNAS
Catalogo de vacunas disponibles.
- **Campos principales:** id_vacuna, nombre, descripcion, intervalo_dias, dosis_requeridas
- **Relacion:** N:1 con ESPECIES (vacunas especificas por especie)

#### Tabla CALENDARIO_VACUNACION
Programacion y registro de vacunaciones.
- **Campos principales:** id_calendario, fecha_programada, fecha_aplicacion, dosis_numero, estado, lote_vacuna
- **Estados:** Pendiente, Aplicada, Vencida, Cancelada
- **Relaciones:**
  - N:1 con MASCOTAS
  - N:1 con VACUNAS
  - N:1 con VETERINARIOS
  - N:1 con USUARIOS (trazabilidad)

#### Tabla SERVICIOS
Catalogo de servicios ofrecidos por la clinica.
- **Campos principales:** id_servicio, codigo, nombre, descripcion, categoria, precio
- **Categorias:** Consulta, Emergencia, Vacunacion, Cirugia, Laboratorio, Estetica, Hospitalizacion, Otro

#### Tabla FACTURAS
Documentos de cobro emitidos.
- **Campos principales:** id_factura, numero_factura, subtotal, descuento, igv, total, estado, metodo_pago
- **Estados:** Pendiente, Pagada, Pago Parcial, Anulada
- **Metodos de pago:** Efectivo, Tarjeta, Transferencia, Yape/Plin, Otro
- **Relaciones:**
  - N:1 con PROPIETARIOS
  - 1:1 con CONSULTAS (opcional)
  - N:1 con MASCOTAS (opcional)

#### Tabla DETALLES_FACTURA
Lineas de detalle de cada factura.
- **Campos principales:** id_detalle, descripcion, cantidad, precio_unitario, descuento, subtotal
- **Relaciones:**
  - N:1 con FACTURAS (con eliminacion en cascada)
  - N:1 con SERVICIOS (opcional)

### Normalizacion Aplicada

1. **Primera Forma Normal (1FN):**
   - Todos los atributos contienen valores atomicos
   - No hay grupos repetitivos
   - Cada tabla tiene una clave primaria definida

2. **Segunda Forma Normal (2FN):**
   - Cumple con 1FN
   - No existen dependencias parciales
   - Los atributos no clave dependen completamente de la clave primaria

3. **Tercera Forma Normal (3FN):**
   - Cumple con 2FN
   - No existen dependencias transitivas
   - Los datos estan organizados en tablas especificas (Especies, Vacunas, Servicios)

### Integridad Referencial

- Todas las relaciones estan definidas con Foreign Keys
- Se utilizan restricciones CHECK para validar estados y tipos
- Indices creados en campos de busqueda frecuente

---

## Guia de Instalacion Paso a Paso

### Requisitos Previos

- Windows 10/11 o Windows Server 2016+
- Python 3.11 o superior
- Microsoft SQL Server 2019 o superior
- ODBC Driver 17 for SQL Server
- Git (opcional)

### Paso 1: Configurar la Base de Datos en SQL Server

1. Abrir **SQL Server Management Studio (SSMS)**

2. Conectarse al servidor SQL Server

3. Abrir el archivo `database/create_database.sql`

4. Ejecutar el script completo (F5 o boton Ejecutar)
   - Este script crea la base de datos `VetCareDB`
   - Crea todas las tablas principales
   - Inserta datos iniciales (especies, vacunas, veterinario de ejemplo)
   - Crea vistas y procedimientos almacenados  
   - Inserta el catalogo de servicios inicial

5. Verificar que las tablas se crearon correctamente:
   ```sql
   USE VetCareDB;
   SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';
   ```

### Paso 2: Clonar o Descargar el Proyecto

Opcion A - Con Git:
```bash
git clone https://github.com/JorgeTurbi/sistemaveterinario.git
cd VetCare_Pro_v2
```

Opcion B - Descarga directa:
- Descargar el archivo ZIP del proyecto
- Extraer en la ubicacion deseada

### Paso 3: Crear el Entorno Virtual

Abrir una terminal (CMD o PowerShell) en la carpeta del proyecto:

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual (Windows CMD)
.venv\Scripts\activate.bat

# O si usas PowerShell
.venv\Scripts\Activate.ps1
```

### Paso 4: Instalar Dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

### Paso 5: Configurar la Conexion a la Base de Datos

1. Abrir el archivo `config.py`

2. Modificar los parametros de conexion segun tu instalacion:

```python
# Nombre del servidor SQL Server
SQL_SERVER = 'localhost'  # o 'NOMBRE_SERVIDOR'

# Nombre de la base de datos
SQL_DATABASE = 'VetCareDB'

# Driver ODBC (verificar cual tienes instalado)
SQL_DRIVER = 'ODBC Driver 17 for SQL Server'
```

3. Configurar la autenticacion:

**Opcion A - Autenticacion de Windows (recomendado):**
```python
params = quote_plus(
    f'DRIVER={{{SQL_DRIVER}}};'
    f'SERVER={SQL_SERVER};'
    f'DATABASE={SQL_DATABASE};'
    f'Trusted_Connection=yes;'
    f'TrustServerCertificate=yes;'
)
```

**Opcion B - Autenticacion SQL Server:**
```python
SQL_USERNAME = 'usuario de tu base de datos'
SQL_PASSWORD = 'tu contrasena'
params = quote_plus(
    f'DRIVER={{{SQL_DRIVER}}};'
    f'SERVER={SQL_SERVER};'
    f'DATABASE={SQL_DATABASE};'
    f'UID={SQL_USERNAME};'
    f'PWD={SQL_PASSWORD};'
    f'TrustServerCertificate=yes;'
)
```

### Paso 6: Ejecutar la Aplicacion

```bash
python run.py
```

Si todo esta configurado correctamente, veras:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Paso 7: Acceder al Sistema

1. Abrir un navegador web

2. Ir a la direccion: `http://127.0.0.1:5000`

3. Crear un usuario administrador inicial o usar las credenciales predeterminadas

---

## Estructura del Proyecto Patron Model View Controller

```
VetCare_Pro_v2/
|
|-- app/
|   |-- __init__.py           # Inicializacion de Flask
|   |-- controllers/          # Controladores (rutas)
|   |   |-- auth_controller.py
|   |   |-- consulta_controller.py
|   |   |-- facturacion_controller.py
|   |   |-- mascota_controller.py
|   |   |-- propietario_controller.py
|   |   |-- reportes_controller.py
|   |   |-- tratamiento_controller.py
|   |   |-- vacunacion_controller.py
|   |   |-- veterinario_controller.py
|   |
|   |-- models/               # Modelos de datos (ORM)
|   |   |-- usuario.py
|   |   |-- mascota.py
|   |   |-- propietario.py
|   |   |-- consulta.py
|   |   |-- tratamiento.py
|   |   |-- vacuna.py
|   |   |-- factura.py
|   |   |-- servicio.py
|   |
|   |-- templates/            # Plantillas HTML (Jinja2)
|   |   |-- base.html
|   |   |-- auth/
|   |   |-- mascotas/
|   |   |-- consultas/
|   |   |-- facturacion/
|   |
|   |-- static/               # Archivos estaticos (CSS, JS, imagenes)
|
|-- database/
|   |-- create_database.sql           # Script principal de BD
|   |-- create_facturacion_tables.sql # Script de facturacion
|
|-- config.py                 # Configuracion de la aplicacion
|-- requirements.txt          # Dependencias del proyecto
|-- run.py                    # Punto de entrada de la aplicacion
|-- README.md                 # Este archivo
```

---

## Funcionalidades Principales

1. **Gestion de Propietarios:** Registro y administracion de clientes
2. **Gestion de Mascotas:** Fichas clinicas de pacientes
3. **Consultas Medicas:** Programacion y atencion de citas
4. **Tratamientos:** Prescripcion y seguimiento
5. **Vacunacion:** Calendario y control de vacunas
6. **Facturacion:** Emision de facturas y control de pagos
7. **Reportes:** Estadisticas y reportes del sistema
8. **Usuarios:** Control de acceso basado en roles

---

## Solucion de Problemas Comunes

### Error: "ODBC Driver not found"
- Instalar ODBC Driver 17 for SQL Server desde Microsoft
- Verificar el nombre del driver en config.py

### Error: "Login failed for user"
- Verificar credenciales en config.py
- Asegurar que SQL Server permite autenticacion mixta
- Verificar que el usuario tiene permisos en la base de datos

### Error: "Cannot connect to server"
- Verificar que SQL Server esta ejecutandose
- Verificar el nombre del servidor en config.py
- Habilitar TCP/IP en SQL Server Configuration Manager

### Error: "Database does not exist"
- Ejecutar primero el script create_database.sql
- Verificar el nombre de la base de datos en config.py

---

## Licencia

Proyecto academico desarrollado para Spain Business School (SBS).
Uso exclusivamente educativo.

---

Fecha de creacion: 2025
Version: 1.0

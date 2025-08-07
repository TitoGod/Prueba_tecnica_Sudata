# Replicación PostgreSQL → Supabase Espejo

Este repositorio contiene el script y la documentación para replicar diariamente los datos de una base PostgreSQL local (`ventas_origen`) hacia una base espejo alojada en Supabase (`ventas_espejo`).

---

## 📁 Estructura del repositorio

```text
Ejercicio 1/
├── replicate.py        # Script Python de replicación
├── create_db.py        # Script Python para crear la base de datos y las tablas en PostgreSQL
├── csv_to_db.py        # Script Python para poblar las tablas con datos
├── .env.example        # Ejemplo de archivo con variables de entorno
├── README.md           # Documentación principal para este ejercicio
└── screenshots/        # Capturas de pantalla del Programador de Tareas en Windows
    └── pasos.png       # Imagenes explicativas
```

---

## 🛠️ Prerrequisitos

1. **Python 3.7+** instalado en tu sistema.
2. **Pip** para instalar dependencias.
3. Cuenta y proyecto creado en **Supabase** (plan gratuito).
4. Base de datos local PostgreSQL (`ventas_origen`) ya creada.

   * Este repositorio incluye un script para la **creación de las tablas** (`create_db.py`).
   * También se incluye un script para **poblar las tablas con datos de ejemplo** (`csv_to_db.py`).

Instalación de librerías Python:

```bash
pip install pandas sqlalchemy psycopg2-binary python-dotenv
```

---

## ⚙️ Configuración de variables de entorno

Copia el archivo de ejemplo y ajusta tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus datos:

```env
# Datos de la base origen (local)
ORIGEN_USER=tu_usuario_local
ORIGEN_PASSWORD=tu_contraseña_local
ORIGEN_HOST=localhost
ORIGEN_PORT=5432
ORIGEN_DB=ventas_origen

# Datos de la base destino (Supabase)
DESTINO_USER=supabase_user
DESTINO_PASSWORD=supabase_pass
DESTINO_HOST=db.supabase.co
DESTINO_PORT=5432
DESTINO_DB=ventas_espejo
```

---

## 📜 Detalle del código (`replicate.py`)

El script realiza los siguientes pasos:

1. **Carga de variables** desde `.env` mediante `python-dotenv`.
2. **Creación de engines** SQLAlchemy para origen y destino.
3. **Reflejo del esquema** de la base local mediante `MetaData().reflect()`.
4. **Recreación del esquema** en Supabase con `drop_all()` y `create_all()`.
5. **Copia de datos** tabla por tabla usando `SELECT` y bulk insert.
6. **Logs** en consola para seguimiento de progreso y errores.

Cada función está documentada con docstrings en el código para facilitar su comprensión y mantenimiento.

---

## 📊 Esquema en la base destino

Para inspeccionar las tablas y relaciones en Supabase:

1. Ingresa al panel de tu proyecto en [https://app.supabase.com](https://app.supabase.com).
2. Selecciona la pestaña **Database → Table Editor**.
3. Verás las tablas reflejadas (`dim_date`, `dim_product`, `dim_customer_segment`, `fact_sales`, etc.) con sus columnas y constraints.
4. Puedes ejecutar queries en **SQL Editor** para explorar datos y relaciones.

### 🖼️ Vista del esquema en Supabase:

![Esquema DB](Ejercicio%201/screenshots/Esquema%20DB.png)

---

## 🕒 Automatización diaria con Programador de Tareas (Windows)

Para automatizar la ejecución diaria del script de replicación (`replicate.py`) desde una base de datos local PostgreSQL hacia Supabase, se utilizó el **Programador de tareas de Windows**.

### 🔧 Requisitos previos

* Tener Python instalado y accesible desde el sistema
* Verificar que el script `replicate.py` funcione correctamente al ejecutarlo manualmente
* Archivo `.env` correctamente configurado y ubicado en la carpeta del script

---

### 📁 Paso 1: Crear un archivo `.bat` para ejecutar el script

Se recomienda usar un archivo por lotes para facilitar la ejecución desde el Programador de tareas.

1. Crear un nuevo archivo de texto y pegar el siguiente contenido:

```bat
@echo off
cd "C:\ruta\a\Ejercicio 1"
"C:\ruta\a\python.exe" replicate.py >> log_replicacion.txt 2>&1
```

> Reemplazar:
>
> * `C:\ruta\a\Ejercicio 1` con la ruta a la carpeta donde está el script.
> * `C:\ruta\a\python.exe` con la ruta real al ejecutable de Python.

2. Guardarlo como `replicar.bat` dentro de la carpeta del proyecto.

Este archivo también generará un log (`log_replicacion.txt`) con cada ejecución, útil para verificar errores.

---

### 🕒 Paso 2: Crear una tarea programada

1. Abrir el **Programador de tareas** (Task Scheduler) desde el menú de inicio.
2. Seleccionar **Crear tarea básica**.
3. Asignar un nombre descriptivo (por ejemplo: `Replicación diaria Supabase`).
4. En **Desencadenar**, seleccionar **Diariamente** y establecer la hora deseada.
5. En **Acción**, seleccionar **Iniciar un programa**.
6. En el campo **Programa o script**, seleccionar el archivo `replicar.bat` creado previamente.
7. Finalizar la tarea.

---

### ✅ Verificación

Para verificar que la tarea funciona correctamente:

* Ejecutar manualmente desde el Programador de tareas (clic derecho → **Ejecutar**).
* Revisar el archivo `log_replicacion.txt` generado para verificar que no haya errores.
* Comprobar que los datos hayan sido replicados correctamente en la base de datos destino (Supabase).

---

### 📌 Notas adicionales

* Asegúrese de que la computadora esté encendida y que no esté en modo de suspensión a la hora programada.
* Si se usan rutas con espacios, colocar entre comillas (`"`) en el archivo `.bat`.
* Si se requiere privilegios administrativos, se puede configurar la tarea para que se ejecute con los mismos.

---

## 🔑 Acceso a la base espejo

Para conectar desde tu aplicación o desde psql:

```bash
psql "postgresql://$DESTINO_USER:$DESTINO_PASSWORD@$DESTINO_HOST:$DESTINO_PORT/$DESTINO_DB"
```

O utiliza el string de conexión que te provee Supabase en **Settings → Database → Connection String**.

---

## 📝 Licencia y contribuciones

Este proyecto está bajo la licencia MIT.

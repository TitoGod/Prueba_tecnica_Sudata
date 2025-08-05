# Repositorio: Replicación PostgreSQL → Supabase Espejo

Este repositorio contiene el script y la documentación para replicar diariamente los datos de una base PostgreSQL local (`ventas_origen`) hacia una base espejo alojada en Supabase (`ventas_espejo`).

---

## 📁 Estructura del repositorio

```text
├── create_db.py       # Script de creación de las tablas en la base de datos PostgreSQL local
├── csv_to_db.py       # Script leer los archivos CSV con pandas, hacer unas transformaciones y luego poblar las tablas en la base de datos local
├── replicate.py       # Script Python de replicación
├── .env               # Variables de entorno
├── README.md          # Documentación principal

```

---

## 🛠️ Prerrequisitos

1. **Python 3.7+** instalado en tu sistema.
2. **Pip** para instalar dependencias.
3. Cuenta y proyecto creado en **Supabase** (plan gratuito).
4. Base de datos local PostgreSQL (`ventas_origen`) ya poblada.

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

---

## 🗓️ Automatización diaria

### Linux/macOS (cron)

1. Asegúrate de que `replicate.py` y `.env` estén accesibles.
2. Haz ejecutable el helper (opcional):

   ```bash
   chmod +x cron_setup.sh
   ```
3. Abre tu crontab:

   ```bash
   crontab -e
   ```
4. Agrega la línea siguiente para ejecutar todos los días a las 02:00 AM:

   ```cron
   0 2 * * * cd /ruta/al/repositorio && /usr/bin/python3 replicate.py >> replicacion.log 2>&1
   ```

### Windows (Task Scheduler)

1. Abre el **Programador de tareas**.
2. Crea una tarea básica con trigger diario a la hora deseada.
3. Acción:

   * Programa/script: ruta a `python.exe` (por ejemplo `C:\Python39\python.exe`)
   * Argumentos: `"C:\ruta\al\repositorio\replicate.py"`
   * "Iniciar en": carpeta del repositorio.

---

## 🔑 Acceso a la base espejo

Para conectar desde tu aplicación o desde psql:

```bash
psql "postgresql://$DESTINO_USER:$DESTINO_PASSWORD@$DESTINO_HOST:$DESTINO_PORT/$DESTINO_DB"
```

O utiliza el string de conexión que te provee Supabase en **Settings → Database → Connection String**.

---

## 📝 Licencia y contribuciones

Este proyecto está bajo la licencia MIT. ¡Contribuciones y mejoras son bienvenidas mediante Pull Requests!

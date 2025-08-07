## 💵 Extracción de Cotizaciones del Dólar (BCRA API → Render)

Este proyecto realiza la carga **histórica** y la **actualización incremental** de cotizaciones del dólar tipo **vendedor** desde la API del BCRA a una base de datos en la nube (Render/PostgreSQL). Ideal para mantener registros actualizados de manera automática.

---

## 📁 Estructura del repositorio

```text
├── incremental.py         # Script de actualización incremental desde la API del BCRA
├── create_db.py           # Script Python para crear la base de datos y las tablas en Supabase
├── csv_to_db.py           # Script Python para poblar las tablas con datos CSV
├── .env.example           # Ejemplo de archivo de variables de entorno
├── README.md              # Documentación principal del proyecto
```

---

### ⚙️ Requisitos

* Python 3.9 o superior
* Cuenta en [Render](https://render.com/)
* Paquetes:

```bash
pip install requests psycopg2-binary python-dotenv
```

---

### 🔐 Variables de entorno

Crear un archivo `.env` con la siguiente información:

```env
DB_HOST=tu_host.supabase.co
DB_PORT=5432
DB_NAME=tu_base_de_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
```

---

### 🧱 Estructura de la tabla

La tabla `cotizaciones` contiene los siguientes campos:

```sql
CREATE TABLE IF NOT EXISTS cotizaciones (
    fecha DATE PRIMARY KEY,
    moneda TEXT,
    tipo_cambio NUMERIC(10,4),
    fuente TEXT
);
```

---


* `data_historica.py`
  Script que toma todos los datos históricos desde la API, se conecta a la base de datos en Render, crea la tabla `cotizaciones` si no existe e inserta todos los datos.

* `incremental.py`
  Script que se conecta a la base de datos en Render, consulta la última fecha registrada y trae solo los nuevos registros posteriores a esa fecha desde la API para insertarlos en la base de datos.

* `utils.py`
  Funciones auxiliares para conexión a base, consulta API y carga de datos.

* `.env`
  Archivo con variables de entorno para conexión local (no subir a repositorio).

---

## 🚀 Cómo fue construida la ingesta incremental

La ingesta incremental está diseñada para mantener actualizada la base de datos con los datos de cotizaciones del BCRA sin duplicar información. El proceso es:

1. Consultar la base de datos para obtener la última fecha registrada.
2. Consultar la API oficial del BCRA solicitando solo los datos posteriores a esa fecha.
3. Insertar únicamente los registros nuevos en la tabla `cotizaciones`, usando cláusulas que evitan duplicados (`ON CONFLICT DO NOTHING`).
4. De esta forma, se minimiza la carga y el tiempo de ejecución, manteniendo la base actualizada.

---

## ⏳ Ejemplo de ejecución

### Ejecución inicial (todo el histórico)

```bash
python data_historica.py
```

Este script descarga y carga la totalidad del histórico desde la API, creando la tabla si es necesario.

---

### Ejecución incremental (solo nuevos datos)

```bash
python incremental.py
```

Este script consulta la última fecha cargada y trae solo los registros posteriores para insertarlos.

---

## 🗄️ Acceso a la base PostgreSQL en la nube (Render)

* La base de datos está alojada en **Render.com**, lo que permite un acceso remoto y estable.
* Las credenciales de conexión (host, puerto, usuario, contraseña, nombre de base) se configuran vía variables de entorno en Render.
* Para acceder a la base y explorar tablas, se puede usar pgAdmin 4 u otras herramientas de cliente PostgreSQL.
* También es posible realizar consultas desde el panel web de Render.

---

## ⏰ Automatización con Render Cron Job

* El script `incremental.py` se ejecuta automáticamente una vez por semana mediante un cron job configurado en Render.
* Esto garantiza que la base de datos esté siempre actualizada sin necesidad de intervención manual.
* Los logs de ejecución y estado del cron job se pueden consultar en el panel de Render.

---


## 📊 Inspección de la base de datos

Para inspeccionar la tabla y sus datos podés usar:

* **pgAdmin 4** o cualquier cliente PostgreSQL, con las variables de entorno indicadas.
* Panel de Render → pestaña de base de datos → Query Editor.

---

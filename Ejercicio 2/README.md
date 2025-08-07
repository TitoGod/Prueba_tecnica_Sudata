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

### 🧠 Funcionalidades

#### 📌 `data_historica.py`

* Descarga **todas las cotizaciones históricas** desde la API del BCRA.
* Crea la tabla `cotizaciones` si no existe.
* Inserta todos los registros en la base de datos.

> ⚠️ Usar una sola vez para inicializar la base de datos.

---

#### 🔁 `incremental.py`

* Consulta la **última fecha** registrada en la base de datos.
* Extrae **nuevos registros** desde la API del BCRA.
* Inserta solo los datos **posteriores a esa fecha**.

> ✅ Ideal para ejecutar de forma programada semanalmente.

---

#### 🔧 `utils.py`

Contiene funciones reutilizables para:

* Conexión a la base de datos
* Inserción de datos
* Llamadas a la API del BCRA
* Manejo de fechas y errores

---

### 🤖 Automatización con GitHub Actions

Podés ejecutar `incremental.py` automáticamente con GitHub Actions, por ejemplo, **una vez por semana**.

#### 1. Crear archivo `.github/workflows/update.yml`:

```yaml
name: Actualización semanal de cotizaciones

on:
  schedule:
    - cron: '0 12 * * 1'  # Todos los lunes a las 12:00 UTC
  workflow_dispatch:      # Permite ejecución manual

jobs:
  run-script:
    runs-on: ubuntu-latest
    steps:
      - name: Clonar repositorio
        uses: actions/checkout@v3

      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Crear archivo .env
        run: |
          echo "DB_HOST=${{ secrets.DB_HOST }}" >> .env
          echo "DB_PORT=${{ secrets.DB_PORT }}" >> .env
          echo "DB_NAME=${{ secrets.DB_NAME }}" >> .env
          echo "DB_USER=${{ secrets.DB_USER }}" >> .env
          echo "DB_PASSWORD=${{ secrets.DB_PASSWORD }}" >> .env

      - name: Ejecutar script incremental
        run: python incremental.py
```

#### 2. Crear los **secretos** en GitHub:

Ir a:
`Settings → Secrets and variables → Actions → New repository secret`
Agregar los siguientes:

* `DB_HOST`
* `DB_PORT`
* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`

---

### ✅ Ejecución manual

```bash
# Carga inicial (una vez)
python data_historica.py

# Actualización incremental
python incremental.py
```

---

### 🧪 Ejemplo de ejecución

```
🔍 Última fecha registrada: 2024-08-01
📅 Consultando desde 2024-08-02 hasta 2025-08-07...
📥 Registros encontrados: 5
✅ Registro insertado: 2024-08-02
✅ Registro insertado: 2024-08-03
...
```

---

### ✅ `.env.example`

```env
# Variables necesarias para conexión a Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_clave_secreta
```

Guardá esto como `.env.example` en la raíz del repositorio.

---

## 🔁 Automatización con GitHub Actions

Este proyecto incluye una configuración para ejecutar el script de ingesta incremental (`incremental.py`) automáticamente una vez por semana usando **GitHub Actions**.

### 📅 Frecuencia

El script se ejecuta automáticamente:

* 🕘 Cada **lunes a las 09:00 (ARG)**.
* ▶️ También puede ser ejecutado **manualmente** desde la pestaña [Actions](../../actions) del repositorio.

### ⚙️ Archivos involucrados

```text
.github/
└── workflows/
    └── run_incremental.yml   # Workflow programado para ejecutar el script semanalmente

.env.example                  # Plantilla para las variables de entorno necesarias
requirements.txt              # Lista de dependencias
```

### 🔐 Configurar Secrets

Debés agregar los siguientes *Secrets* en tu repositorio GitHub:

1. `SUPABASE_URL`: URL del proyecto Supabase
2. `SUPABASE_KEY`: API Key o clave de servicio para la conexión

> Configuralos en: **Settings → Secrets and variables → Actions**

### ✅ Resultado

Cada semana, GitHub ejecutará el flujo de trabajo que:

1. Clona tu repo.
2. Instala dependencias.
3. Crea un archivo `.env` temporal a partir de los secretos.
4. Ejecuta `incremental.py` para insertar nuevas cotizaciones en la base.

---


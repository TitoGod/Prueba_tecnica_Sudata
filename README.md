# Repositorio de Prueba Técnica Sudata

Este repositorio contiene la resolución de distintos ejercicios como parte de una prueba técnica. Cada ejercicio se encuentra organizado en su propia carpeta con código fuente, scripts, y un `README.md` explicativo.

---

## 📁 Estructura general

```text
Ejercicio 1/
├── replicate.py        # Script Python de replicación
├── create_db.py        # Script Python para crear la base de datos y las tablas en PostgreSQL
├── csv_to_db.py        # Script Python para poblar las tablas con datos
├── .env.example        # Ejemplo de archivo con variables de entorno
├── README.md           # Documentación principal para este ejercicio
└── screenshots/        # Capturas de pantalla del Programador de Tareas en Windows
    ├── Esqueda DB      # Screenshot del esquema creado en Supabase
    └── pasos.png       # Imagenes explicativas

Ejercicio 2/
├── data_historica.py   # Script principal para extraer las cotizaciones históricas desde la API del BCRA
├── incremental.py      # Script para ingresar los nuevos datos a partir de la ultima fecha registrada en la base de datos
├── utils.py            # Todas las funciones necesarias para mantener el código limpio y escalable
├── .env.example        # Ejemplo con variables necesarias
└── README.md           # Documentación detallada del Ejercicio 2

Ejercicio 3/
├── .env                 # variables de entorno (no subir)
├── bloqueos_tecnicos.py # detectar Cloudflare / CAPTCHA / rate-limits
├── csv_to_db_supabase.py# leer CSV, limpiar/transformar y cargar a Supabase
├── permite_scrap.py     # comprobar robots.txt / permiso de crawling
├── scraping.py          # scraper para Argenprop (genera CSV)
└── README.md            # Documentación específica del Ejercicio 3

└── README.md           # Este README global
````

---

## 📌 Contenidos por ejercicio

### 🔹 Ejercicio 1: Replicación PostgreSQL → Supabase

* Crear una base PostgreSQL local (`ventas_origen`)
* Crear y poblar tablas con datos desde CSV
* Replicar los datos a una base espejo en Supabase (`ventas_espejo`)
* Automatizar la replicación diaria con Task Scheduler (Programador de Tareas de Windows)

Ver [Ejercicio 1/README.md](Ejercicio%201/README.md) para más detalles.

---

### 🔹 Ejercicio 2: Extracción incremental desde la API del BCRA usando Render cron jobs

* Se conecta a la [API oficial del BCRA](https://www.bcra.gob.ar/BCRAyVos/catalogo-de-APIs-banco-central.asp) para obtener las cotizaciones del dólar tipo vendedor.
* La extracción es **incremental**, es decir, se descarga solo la información nueva desde la última fecha registrada.
* Se utiliza una base PostgreSQL en la nube desplegada en **Render**.
* La actualización semanal se realiza mediante un **cron job configurado en Render** (sin necesidad de Task Scheduler ni GitHub Actions).

Ver [Ejercicio 2/README.md](Ejercicio%202/README.md) para más detalles.

---

### 🔹 Ejercicio 3: Web Scraping → Limpieza → Carga a Supabase

* Incluye scripts para comprobar permisos en robots.txt y detectar bloqueos técnicos antes de realizar el scraping.
* Scraping de listados públicos (ej. Argenprop — terrenos/venta/posadas) con Selenium. 
* Limpieza y transformación del CSV resultante del scraping y carga en base de datos PostgreSQL alojada en Supabase.
* El flujo recomendado es: verificar permisos → detectar bloqueos → ejecutar scraping → cargar datos a Supabase.

Ver [Ejercicio 3/README.md](Ejercicio%203/README.md) para más detalles.

---

## ✅ Recomendaciones de uso

* Ingresar a cada carpeta de ejercicio para acceder a sus scripts y documentación específica.
* Usar entornos virtuales para instalar dependencias locales.

---

## 📄 Licencia

Este repositorio está disponible bajo la licencia MIT.
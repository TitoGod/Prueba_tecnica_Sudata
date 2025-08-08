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

<<<<<<< HEAD
Ejercicio 3/
├── .env                 # variables de entorno (no subir)
├── bloqueos_tecnicos.py # detectar Cloudflare / CAPTCHA / rate-limits
├── csv_to_db_supabase.py# leer CSV, limpiar/transformar y cargar a Supabase
├── permite_scrap.py     # comprobar robots.txt / permiso de crawling
├── scraping.py          # scraper para Argenprop (genera CSV)
└── README.md            # Documentación específica del Ejercicio 3

=======
>>>>>>> 9a8f206c1285824160e2575ba4d106a51139baae
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

### 🔹 Ejercicio 3: Scraping responsable → Limpieza → Carga a Supabase

**Resumen:** herramientas y scripts para comprobar permisos y bloqueos técnicos, raspar listados públicos (ej. Argenprop — `terrenos/venta/posadas`), limpiar/transformar el CSV resultante y cargarlo a una base Postgres alojada en **Supabase**.

**Qué contiene la carpeta `Ejercicio 3/`:**

* **`.env`** — variables de entorno (no subir al repo). Variables esperadas:
  `SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`, `SUPABASE_DB_HOST`, `SUPABASE_DB_PORT`, `SUPABASE_DB_NAME`.

* **`permite_scrap.py`** — comprueba `robots.txt` y ayuda a interpretar si la ruta objetivo está permitida para crawling con un user-agent dado. Es la primera verificación recomendada antes de raspar.

* **`bloqueos_tecnicos.py`** — pruebas técnicas que detectan bloqueos: códigos HTTP (403/429/503), cabeceras Cloudflare / `cf-`, texto de desafío (CAPTCHA), etc. Sirve para saber si el sitio aplica protección anti-bot.

* **`scraping.py`** — scraper principal (Selenium + utilidades). Funciones principales:

  * `init_driver(headless=True)`: inicializa Chrome con opciones (headless opcional, user-agent, evasión básica de `navigator.webdriver`).
  * `close_cookies_if_present(driver)`, `scroll_page(driver)`, `extract_cards_on_page(driver)`, `click_next_page(driver)` — helpers para interactuar con la página y extraer tarjetas.
  * Genera un CSV con columnas crudas: `precio_raw`, `moneda`, `ubicacion`, `titulo_primary`, `detalle_url`, etc.

* **`csv_to_db_supabase.py`** — lee el CSV, aplica transformaciones (normaliza nombres de columna, filtra filas sin `moneda`, convierte `precio` a `int`, agrega `id` secuencial) y carga a Supabase usando **SQLAlchemy**. Crea la tabla si no existe y usa `INSERT ... ON CONFLICT DO NOTHING` por defecto.

**Flujo recomendado (resumido):**

1. Revisar Términos y Condiciones y ejecutar `permite_scrap.py`.
2. Ejecutar `bloqueos_tecnicos.py --url "<tu_url_objetivo>"`.
3. Si está permitido y no hay bloqueos severos, ejecutar `scraping.py` → generar CSV.
4. Ajustar `.env` con credenciales Supabase y ejecutar `csv_to_db_supabase.py` → datos en Supabase.

**Nota legal / buenas prácticas:** incluso si los avisos son visibles públicamente, los Términos pueden prohibir la extracción automatizada. Pedir permiso por escrito (ej. `info@argenprop.com`) antes de raspar a gran escala o uso comercial. Respetar `robots.txt`, `crawl-delay` y no evadir CAPTCHAs.

Ver [Ejercicio 3/README.md](Ejercicio%203/README.md) para la documentación completa del ejercicio 3 (comandos, ejemplos y troubleshooting).

---

## ✅ Recomendaciones de uso

* Ingresar a cada carpeta de ejercicio para acceder a sus scripts y documentación específica.
* Usar entornos virtuales para instalar dependencias locales.
* Documentar cada nuevo ejercicio agregando su propia carpeta y README.
* Mantener el archivo `.env` fuera del control de versiones (añadirlo a `.gitignore`).

---

## 📄 Licencia

Este repositorio está disponible bajo la licencia MIT.
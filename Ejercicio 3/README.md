# Ejercicio 3 — Scraping y carga a Supabase

**Resumen corto:** este ejercicio contiene scripts para:

* comprobar si está permitido hacer scraping (`permite_scrap.py`),
* detectar bloqueos técnicos / Cloudflare (`bloqueos_tecnicos.py`),
* realizar el scraping en Argenprop (`scraping.py`),
* limpiar/transformar el CSV resultado y cargarlo en una base Postgres en **Supabase** (`csv_to_db_supabase.py`).


# Estructura del proyecto

```
Ejercicio 3
├── .env.example              # variables de entorno de ejemplo (para modificar)
├── bloqueos_tecnicos.py      # detecta Cloudflare/CAPTCHAs/limitaciones técnicas
├── csv_to_db_supabase.py     # lee CSV, limpia/transforma y carga a Supabase (Postgres) usando SQLAlchemy
├── permite_scrap.py          # chequea robots.txt y permiso de crawling básico
└── scraping.py               # scraper principal para Argenprop (genera CSV)
```

---

# Requisitos / Instalación

* Python 3.9+ (probado en 3.11)
* Crear un entorno virtual (recomendado):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

* Instalar dependencias:


```bash
pip install pandas python-dotenv sqlalchemy psycopg2-binary requests beautifulsoup4 webdriver-manager selenium dnspython
```

---

# Descripción de cada archivo y uso

## `permite_scrap.py`

* **Qué hace:** consulta `robots.txt` del dominio (ej. `argenprop.com`) y devuelve si la ruta objetivo puede ser rastreada por un user-agent dado. También busca indicios en Términos y Condiciones (si pegás o cargas el texto).
* **Uso:**

```bash
python permite_scrap.py
```

* **Salida típica:** indica `can_fetch` (True/False) y muestra reglas `Disallow` / `Crawl-delay` si existen.
* **Nota:** `robots.txt` es guía técnica — no sustituye a los Términos y Condiciones. Revisá ambos.

---

## `bloqueos_tecnicos.py`

* **Qué hace:** hace peticiones de prueba contra la URL objetivo y analiza cabeceras/respuestas para detectar:

  * códigos HTTP 403 / 429 / 503,
  * cabeceras `Server` o `cf-` (Cloudflare),
  * HTML con frases tipo `Attention required` o `recaptcha`.
* **Uso:**

```bash
python bloqueos_tecnicos.py --url "https://www.argenprop.com/terrenos/venta/posadas"
```

* **Salida típica:** muestra `status_code`, cabeceras relevantes y si detectó posible CAPTCHA/protección.

---

## `scraping.py`

* **Qué hace:** script principal que utiliza Selenium (o requests/BS4) para navegar la(s) página(s) objetivo y extraer tarjetas de inmuebles. Genera un CSV con columnas crudas (`precio_raw`, `moneda`, `ubicacion`, `titulo_primary`, `detalle_url`, etc.).
* **Notas de diseño:**

  * Implementa `init_driver(headless=True)` para configurar Chrome (con `navigator.webdriver` oculto).
  * Tiene funciones auxiliares: `close_cookies_if_present`, `scroll_page`, `extract_cards_on_page`, `click_next_page`.
  * Está pensado para recorrer la primer y segunda página y guardar hasta 40 registros (configurable en el script).
* **Ejecutar:**

```bash
python scraping.py
```

* **Salida:** CSV (ruta definida en el script, p. ej. `salida.csv` o la que pongas en `CSV_DEFAULT`).

**Importante:** respetá tiempos de espera y no evadir CAPTCHAs.

---

## `csv_to_db_supabase.py`

* **Qué hace:** lee el CSV generado por `scraping.py`, limpia y transforma columnas y carga los datos en la tabla destino en Supabase/Postgres usando SQLAlchemy.
* **Transformaciones aplicadas:**

  1. Normaliza nombres de columnas (`precio`, `moneda`, `ubicacion`, `titulo`, `detalle_url`).
  2. Elimina filas donde `moneda` es nula o placeholders (`"Missing value"`, `"nan"`, etc.).
  3. Limpia `precio`: quita puntos/comas/símbolos y convierte a `int`. Si no queda dígito, queda `NULL`.
  4. Agrega una columna `id` consecutiva **después** de filtrar moneda (1,2,3...).
* **Creación de tabla:** si la tabla no existe, la crea con esquema solicitado:

```sql
CREATE TABLE terrenos (
  id INTEGER PRIMARY KEY,
  precio INTEGER,
  moneda VARCHAR(10),
  ubicacion VARCHAR(200),
  titulo VARCHAR(200),
  detalle_url VARCHAR(300)
);
```

* **Carga:** inserta con `INSERT ... ON CONFLICT (id) DO NOTHING` (evita errores si `id` ya existe). Opcionalmente se podría hacer `ON CONFLICT DO UPDATE` si preferís upsert.
* **Uso:**

```bash
python csv_to_db_supabase.py
```

* **CSV por defecto:** la ruta al CSV está definida en la variable `CSV_DEFAULT` al inicio del script. Podés editarla o pasar otra ruta si el script tiene argparser (según la versión que uses).

---

# Ejemplo de flujo recomendado

1. **Verificá permiso**

   * Ejecutá `permite_scrap.py` y leé los Términos (contactá si es necesario).

2. **Comprobá limitaciones técnicas**

   * `python bloqueos_tecnicos.py --url "https://www.argenprop.com/terrenos/venta/posadas"`

3. **Scrapear (si tenés permiso)**

   * `python scraping.py` → genera CSV (ej. `terrenos_argenprop_posadas.csv`)

4. **Transformar & Cargar**

   * Editá `.env` con tus credenciales Supabase.
   * `python csv_to_db_supabase.py` → crea tabla (si hace falta) y carga datos.

5. **Verificar en Supabase**

   * Conectá a la consola de Supabase y verificá la tabla `terrenos` (o el nombre que hayas usado).

---

# Buenas prácticas y recomendaciones

* **Pausas y throttling:** evitar sobrecargar el sitio. 1–3 segundos entre requests es una buena base (ajustá según `robots.txt` y acuerdo).
* **User-Agent identificable:** usá un `User-Agent` que incluya contacto (ej. `MiScraper/1.0 (+mailto:tu@mail.com)`).
* **No evadir protecciones:** nunca evadir CAPTCHAs o medidas anti-bot.
* **No recolectar datos personales innecesarios** y cumplí leyes locales (Ley 25.326 en Argentina).
* **Logs y rate limits:** guardá logs de actividad y respetá límites.
* **Permisos:** si pensás usar los datos comercialmente, pedí un acuerdo/licencia.

---

# Ejemplos de comandos útiles

* Ejecutar scraper:

```bash
python scraping.py
```

* Probar robots:

```bash
python permite_scrap.py --url "https://www.argenprop.com/terrenos/venta/posadas"
```

* Analizar bloqueos:

```bash
python bloqueos_tecnicos.py --url "https://www.argenprop.com/terrenos/venta/posadas"
```

* Cargar CSV a Supabase:

```bash
python csv_to_db_supabase.py
```

---

# Estado / notas finales

* **Objetivo del ejercicio:** practicar pipeline completo: *scraping → limpieza → carga a Postgres (Supabase)* con validaciones técnicas y legales.
* El repo incluye **herramientas para chequear permiso y bloqueos** para operar responsablemente.

---
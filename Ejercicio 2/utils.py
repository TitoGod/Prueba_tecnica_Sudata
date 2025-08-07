# Archivo con todas las funciones necesarias para la conexión a la base de datos, la obtención de datos históricos
# y la inserción de datos en la base de datos.

# Importar las librerías necesarias
import os
import requests
from datetime import date, datetime, timedelta
import ssl
import urllib3
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ─── CONFIGuración SSL (solo para desarrollo) ───────────────────────────────
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# ────────────────────────────────────────────────────────────────────────────

# Configuración de la API del BCRA
API_BASE = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0"
MONEDA = "USD"

# Variables de entorno
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# ──────────────────────── Funciones  ────────────────────────

def connect_db():
    """
    Crea una conexión a la base de datos PostgreSQL en Supabase.
    """
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
    )
    conn.autocommit = True
    return conn

def create_table(conn):
    """
    Crea la tabla cotizaciones si no existe.
    """
    sql = '''
    CREATE TABLE IF NOT EXISTS cotizaciones (
        fecha DATE PRIMARY KEY,
        moneda TEXT,
        tipo_cambio NUMERIC(10,4),
        fuente TEXT
    );
    '''
    with conn.cursor() as cur:
        cur.execute(sql)

def fetch_range(fecha_desde, fecha_hasta, limit=1000):
    """Trae una página de cotizaciones entre fecha_desde y fecha_hasta."""
    results = []
    offset = 0
    while True:
        resp = requests.get(
            f"{API_BASE}/Cotizaciones/{MONEDA}",
            params={
                "fechaDesde": fecha_desde,
                "fechaHasta": fecha_hasta,
                "limit": limit,
                "offset": offset
            },
            headers={"Accept": "application/json"},
            verify=False
        )
        # Si el rango no existe o es inválido, cortamos
        if resp.status_code == 400:
            break
        resp.raise_for_status()
        page = resp.json().get("results", [])
        if not page:
            break
        results.extend(page)
        offset += limit
    return results

def fetch_all_historical(start_year=2024):
    """Recorre año a año desde start_year hasta hoy y acumula todo el histórico."""
    today = date.today()
    all_data = []
    for year in range(start_year, today.year + 1):
        desde = f"{year}-01-02"
        hasta = f"{year}-12-31" if year < today.year else today.isoformat()
        print(f"🔄 Obteniendo {year}: {desde} → {hasta}")
        page = fetch_range(desde, hasta)
        print(f"   • Registros: {len(page)}")
        all_data.extend(page)
    return all_data

def insert_data_to_db(conn, data):
    """
    Inserta los datos de cotizaciones en la base de datos.
    Si la fecha ya existe, ignora el registro.
    """
    with conn.cursor() as cur:
        for entry in data:
            fecha = entry["fecha"]
            valor = entry["detalle"][0]["tipoCotizacion"]

            try:
                cur.execute(
                    '''
                    INSERT INTO cotizaciones (fecha, moneda, tipo_cambio, fuente)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (fecha) DO NOTHING;
                    ''',
                    (fecha, "Dólar", valor, "BCRA")
                )
            except Exception as e:
                print(f"❌ Error insertando {fecha}: {e}")

        conn.commit()
        print("✅ Todos los datos fueron insertados correctamente.")


def get_last_date(conn):
    """
    Obtiene la última fecha registrada en la base de datos.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT MAX(fecha) FROM cotizaciones;")
        result = cur.fetchone()
        return result[0]  # Puede ser None si la tabla está vacía
    

def fetch_from_date(last_date):
    """
    Consulta la API del BCRA desde la última fecha registrada hasta hoy.
    """
    fecha_desde = (last_date + timedelta(days=1)).isoformat()
    fecha_hasta = datetime.today().date().isoformat()
    
    print(f"📅 Consultando cotizaciones desde {fecha_desde} hasta {fecha_hasta}...")
    
    data = fetch_range(fecha_desde, fecha_hasta)
    print(f"📥 Registros encontrados: {len(data)}")
    
    return data


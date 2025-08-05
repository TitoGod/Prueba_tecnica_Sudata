# Ejercicio 1: Script para crear base de datos y tablas en PostgreSQL
# Este script crea una base de datos llamada 'ventas_origen' y un rol 'bi_user',
# y define las tablas DimDate, DimCustomerSegment, DimProduct y FactSales con sus
# respectivas columnas y tipos de datos ajustados según las especificaciones.
# Requiere la librería psycopg2 para conectarse a PostgreSQL.

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()  # Busca automáticamente el archivo .env en el directorio actual

# Parámetros de conexión al servidor
PG_HOST     = os.getenv('PG_HOST')
PG_PORT     = os.getenv('PG_PORT')
PG_SUPERDB  = os.getenv('PG_SUPERDB')
PG_SUPERUSR = os.getenv('PG_SUPERUSR')
PG_SUPERPW  = os.getenv('PG_SUPERPW')

# Nombre de la nueva base de datos y su dueño
NEW_DB      = os.getenv('NEW_DB')
NEW_OWNER   = os.getenv('NEW_OWNER')
NEW_OW_PW   = os.getenv('NEW_OW_PW')

# DDL para las tablas
# Las tablas se crean con los tipos de datos ajustados según las especificaciones
# y se utilizan los nombres de columnas en minúsculas y con guiones bajos según las convenciones de PostgreSQL.
# Las claves foráneas se definen correctamente para referenciar las tablas correspondientes.

TABLE_DDL = {
    "dim_date": """
        CREATE TABLE IF NOT EXISTS dim_date (
          date_id      INTEGER PRIMARY KEY,
          date         DATE   NOT NULL,
          year         INTEGER,
          quarter      INTEGER,
          quarter_name  VARCHAR(10),
          month        INTEGER,
          month_name    VARCHAR(20),
          day          INTEGER,
          week_day      INTEGER,
          week_day_name  VARCHAR(20)
        );
    """,
    "dim_customer_segment": """
        CREATE TABLE IF NOT EXISTS dim_customer_segment (
          segment_id  INTEGER PRIMARY KEY,
          city        VARCHAR(100)
        );
    """,
    "dim_product": """
        CREATE TABLE IF NOT EXISTS dim_product (
          product_id    INTEGER PRIMARY KEY,
          product_type  VARCHAR(100)
        );
    """,
    "fact_sales": """
        CREATE TABLE IF NOT EXISTS fact_sales (
          sales_id        VARCHAR(20) PRIMARY KEY,
          date_id         INTEGER REFERENCES dim_date(date_id),
          product_id      INTEGER REFERENCES dim_product(product_id),
          segment_id      INTEGER REFERENCES dim_customer_segment(segment_id),
          price_per_unit  NUMERIC(12,2),
          quantity_sold   INTEGER
        );
    """
}

def create_database():
    """Se conecta al servidor en la base 'postgres' y crea la DB + rol bi_user."""
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT,
        dbname=PG_SUPERDB,
        user=PG_SUPERUSR, password=PG_SUPERPW
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # 1. Crear rol bi_user si no existe
    cur.execute(sql.SQL(
        "DO $$ BEGIN "
        "   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = %s) THEN "
        "     CREATE ROLE {rol} WITH LOGIN PASSWORD %s; "
        "   END IF; "
        "END $$;"
    ).format(rol=sql.Identifier(NEW_OWNER)),
    [NEW_OWNER, NEW_OW_PW])
    
    # 2. Crear base ventas_origen
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", [NEW_DB])
    if not cur.fetchone():
        cur.execute(sql.SQL(
            "CREATE DATABASE {db} OWNER {rol} "
            "ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8' TEMPLATE template0;"
        ).format(
            db=sql.Identifier(NEW_DB),
            rol=sql.Identifier(NEW_OWNER)
        ))
        print(f"Base de datos '{NEW_DB}' creada exitosamente.")
    else:
        print(f"La base '{NEW_DB}' ya existe.")
    
    cur.close()
    conn.close()

def create_tables():
    """Se conecta a ventas_origen como bi_user y ejecuta los DDL ajustados."""
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT,
        dbname=NEW_DB,
        user=NEW_OWNER, password=NEW_OW_PW
    )
    cur = conn.cursor()
    for name, ddl in TABLE_DDL.items():
        print(f"Creando tabla {name}...")
        cur.execute(ddl)
    conn.commit()
    cur.close()
    conn.close()
    print("Tablas creadas correctamente.")

if __name__ == "__main__":
    create_database()
    create_tables()

# Lee el CSV de terrenos en Posadas, Misiones. Luego limpia/transforma las columnas y carga los datos
# a una tabla Postgres en Supabase usando SQLAlchemy (con SSL requerido).

# Importar las librerías necesarias
import os
import re
import sys
from typing import Dict
from dotenv import load_dotenv

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert as pg_insert


# CONFIG: Ruta CSV por defecto
CSV_DEFAULT = r"C:/Users/Dario/Desktop/Prueba técnica Sudata/Ejercicio 3/terrenos_posadas.csv"

# Cargar .env y configurar conexiones
load_dotenv()

DESTINO = {
    'user': os.getenv('SUPABASE_DB_USER'),
    'password': os.getenv('SUPABASE_DB_PASSWORD'),
    'host': os.getenv('SUPABASE_DB_HOST'),
    'port': os.getenv('SUPABASE_DB_PORT', '5432'),
    'database': os.getenv('SUPABASE_DB_NAME')
}

# Validación mínima de variables
if not all([DESTINO.get(k) for k in ('user','password','host','port','database')]):
    print("❌ Faltan variables SUPABASE_* en el .env. Revisá SUPABASE_DB_USER, _PASSWORD, _HOST, _PORT, _NAME")
    sys.exit(1)

def make_engine(cfg: Dict) -> Engine:
    """
    Construye un engine SQLAlchemy para Postgres (psycopg2).
    Incluye sslmode='require' en connect_args (importante para Supabase).
    """
    uri = f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    engine = create_engine(uri, echo=False, pool_pre_ping=True, connect_args={"sslmode": "require"})
    return engine


# Funciones de transformación

def clean_moneda(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas donde 'moneda' sea nula o placeholder (Missing value, etc.)."""
    def is_missing(x):
        if pd.isna(x):
            return True
        s = str(x).strip().lower()
        return s == "" or s in {"missing value", "missing", "nan", "none", "null"}
    mask_valid = ~df["moneda"].apply(is_missing)
    before = len(df)
    df = df[mask_valid].copy()
    after = len(df)
    print(f"Filas antes del filtro moneda: {before} -> después: {after} (se eliminaron {before-after})")
    df["moneda"] = df["moneda"].astype(str).str.strip()
    return df

def clean_precio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Quita caracteres no numéricos y convierte a int (nullable).
    Ej: "140.000" -> 140000
    """
    def parse_price(x):
        if pd.isna(x):
            return pd.NA
        s = str(x).strip()
        digits = re.sub(r"[^\d]", "", s)
        if digits == "":
            return pd.NA
        try:
            return int(digits)
        except:
            return pd.NA
    df["precio"] = df["precio"].apply(parse_price)
    df["precio"] = df["precio"].astype("Int64")  # entero nullable
    n_null = df["precio"].isna().sum()
    print(f"Precios no convertibles a int: {n_null} filas (serán NULL en DB)")
    return df

def add_sequential_id(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega columna id incremental empezando en 1 (después de filtrar)."""
    df = df.reset_index(drop=True)
    df.insert(0, "id", (df.index + 1).astype(int))
    return df


# DB: crear tabla e insertar con upsert (ON CONFLICT DO NOTHING)

def create_table_if_not_exists(engine: Engine, table_name: str = "terrenos_posadas"):
    """Crea la tabla con el esquema pedido si no existe."""
    metadata = MetaData()
    table = Table(
        table_name, metadata,
        Column("id", Integer, primary_key=True),
        Column("precio", Integer, nullable=True),
        Column("moneda", String(10), nullable=True),
        Column("ubicacion", String(200), nullable=True),
        Column("titulo", String(200), nullable=True),
        Column("detalle_url", String(300), nullable=True),
    )
    metadata.create_all(engine, checkfirst=True)
    print(f"Tabla '{table_name}' creada.")
    return table, metadata

def insert_dataframe(engine: Engine, table: Table, df: pd.DataFrame):
    """
    Inserta rows del DataFrame usando INSERT ... ON CONFLICT DO NOTHING para evitar
    errores si el id ya existe.
    """
    # preparar lista de diccionarios
    records = []
    for _, r in df.iterrows():
        records.append({
            "id": int(r["id"]),
            "precio": None if pd.isna(r["precio"]) else int(r["precio"]),
            "moneda": None if pd.isna(r["moneda"]) else str(r["moneda"]),
            "ubicacion": None if pd.isna(r["ubicacion"]) else str(r["ubicacion"]),
            "titulo": None if pd.isna(r["titulo"]) else str(r["titulo"]),
            "detalle_url": None if pd.isna(r["detalle_url"]) else str(r["detalle_url"])
        })

    if not records:
        print("No hay registros para insertar.")
        return

    conn = engine.connect()
    trans = conn.begin()
    try:
        # pg_insert permite on_conflict_do_nothing
        stmt = pg_insert(table).values(records)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        result = conn.execute(stmt)
        trans.commit()
        print(f"Insertadas {len(records)} filas.")
    except SQLAlchemyError as e:
        trans.rollback()
        print("❌ Error insertando registros:", e)
        raise
    finally:
        conn.close()


# MAIN

def main(csv_path: str = None, table_name: str = "terrenos_posadas"):
    # Usar csv_path proporcionado o la ruta por defecto
    csv_path = csv_path or CSV_DEFAULT
    print("Leyendo CSV:", csv_path)
    df = pd.read_csv(csv_path, dtype=str)

    # Transformaciones
    df = clean_moneda(df)
    df = clean_precio(df)
    df = add_sequential_id(df)

    # Seleccionar columnas finales en orden
    final_cols = ["id", "precio", "moneda", "ubicacion", "titulo", "detalle_url"]
    df_final = df[final_cols].copy()

    # Conectar a la DB destino (Supabase)
    print("Conectando a Supabase/Postgres (DESTINO)...")
    try:
        engine_dest = make_engine(DESTINO)
        # chequeo simple
        with engine_dest.connect() as c:
            c.execute(text("SELECT 1")).fetchone()
        print("Conexión establecida con DESTINO.")
    except Exception as e:
        print("❌ Error conectando al destino:", e)
        raise

    # Crear tabla si no existe e insertar
    table_obj, metadata = create_table_if_not_exists(engine_dest, table_name)
    insert_dataframe(engine_dest, table_obj, df_final)

    # Cerrar engine
    engine_dest.dispose()
    print("Proceso finalizado.")

if __name__ == "__main__":
    main()

# Replicación incremental de datos históricos
# Importar las librerías necesarias

import os
import requests
from datetime import date
import ssl
import urllib3
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from utils import connect_db, insert_data_to_db, get_last_date, fetch_from_date

# Función principal para ejecutar el script

if __name__ == "__main__":
    print("🚀 Iniciando replicación incremental...")

    # 1. Conexión a la base
    conn = connect_db()

    # 2. Obtener última fecha en la base
    last_date = get_last_date(conn)
    print(f"🕒 Última fecha registrada en DB: {last_date}")

    # 4. Traer sólo los nuevos registros
    new_data = fetch_from_date(last_date)
    print(f"📈 Nuevos registros a insertar: {len(new_data)}")

    # 5. Insertar nuevos datos
    if new_data:
        insert_data_to_db(conn, new_data)
    else:
        print("✅ La base de datos ya está actualizada.")

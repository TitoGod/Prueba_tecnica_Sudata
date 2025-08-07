# Cotizaciones del BCRA
# Este script obtiene las cotizaciones del dólar vendedor del BCRA y las almacena en
# una base de datos PostgreSQL en la nube (Supabase). Utiliza variables de entorno para la configuración.

# Importar las librerías necesarias

import os
import requests
from datetime import date
import ssl
import urllib3
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from utils import connect_db, fetch_all_historical, insert_data_to_db, create_table

# Función principal para ejecutar el script

if __name__ == "__main__":
    # 1. Obtener todos los datos históricos desde la API del BCRA
    data = fetch_all_historical()
    print(f"\n✅ Total histórico: {len(data)} registros")

    # 2. Conectar a la base de datos PostgreSQL (Supabase)
    conn = connect_db()

    # 3. Crear la tabla si no existe
    create_table(conn)

    # 4. Insertar los datos históricos en la base de datos
    insert_data_to_db(conn, data)

    # 5. Mostrar los últimos 5 registros (más recientes)
    data_sorted = sorted(data, key=lambda x: x["fecha"])
    últimos5 = data_sorted[-5:]

    print("Últimos 5 cotizaciones (de más reciente a más antigua):")
    for entry in reversed(últimos5):
        fecha = entry["fecha"]
        valor = entry["detalle"][0]["tipoCotizacion"]
        print(f"  • Fecha: {fecha} | Valor: {valor}")
    
    # Cerrar la conexión a la base de datos
    conn.close()


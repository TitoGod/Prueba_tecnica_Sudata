# Importar librerías necesarias

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()  # Busca automáticamente el archivo .env en el directorio actual

# Variables de conexión a la base de datos
DB_USER     = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST     = os.getenv('DB_HOST')
DB_PORT     = os.getenv('DB_PORT')
DB_NAME     = os.getenv('DB_NAME')

# 📌 Conexión a PostgreSQL
conexion = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#  Función para insertar CSV en PostgreSQL y mapear columnas
def insertar_csv_en_postgres(csv_path, tabla_destino, mapeo_columnas, conexion_string):
    try:
        print(f'🔄 Procesando archivo: {csv_path}')

        df = pd.read_csv(csv_path)
        df.rename(columns=mapeo_columnas, inplace=True)

        engine = create_engine(conexion_string)
        df.to_sql(tabla_destino, engine, if_exists='append', index=False)

        print(f"✅ Datos insertados correctamente en la tabla '{tabla_destino}'\n")
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {csv_path}\n")
    except Exception as e:
        print(f"❌ Error al insertar datos en '{tabla_destino}': {e}\n")


# 📂 Ruta base donde están los archivos CSV
ruta_base = r'C:/Users/Dario/Desktop/Prueba técnica Sudata/Ejercicio 1' 

# 📁 Archivos a procesar
archivos = [
        {
        'archivo': 'DimDate.csv',
        'tabla': 'dim_date',
        'mapeo': {
            'dateid': 'date_id',
            'date': 'date',
            'Year': 'year',
            'Quarter': 'quarter',
            'QuarterName': 'quarter_name',
            'Month': 'month',
            'Monthname': 'month_name',
            'Day': 'day',
            'Weekday': 'week_day',
            'WeekdayName': 'week_day_name'
        }
    },
    {
        'archivo': 'DimProduct.csv',
        'tabla': 'dim_product',
        'mapeo': {
            'Productid': 'product_id',
            'Producttype': 'product_type'
        }
    },
    {
        'archivo': 'DimCustomerSegment.csv',
        'tabla': 'dim_customer_segment',
        'mapeo': {
            'Segmentid': 'segment_id',
            'City': 'city'
        }
    },
        {
        'archivo': 'FactSales.csv',
        'tabla': 'fact_sales',
        'mapeo': {
            'Salesid': 'sales_id',
            'Dateid': 'date_id',
            'Productid': 'product_id',
            'Segmentid': 'segment_id',
            'Price_PerUnit': 'price_per_unit',
            'QuantitySold': 'quantity_sold'
        }
    }
]

# 🔁 Ejecutar proceso para cada archivo
for item in archivos:
    path_completo = os.path.join(ruta_base, item['archivo'])
    insertar_csv_en_postgres(
        csv_path=path_completo,
        tabla_destino=item['tabla'],
        mapeo_columnas=item['mapeo'],
        conexion_string=conexion
    )

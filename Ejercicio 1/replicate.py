"""
Script para replicar diariamente toda la base de datos PostgreSQL 'ventas_origen'
hacia una base espejo alojada en Supabase, con orden controlado de tablas.

Orden definido de replicación (primero dimensiones, luego hechos)
Manejo mejorado de errores
Verificación de dependencias
"""

import os
from typing import List, Dict
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv

# -------------------------------------------------------------------
#  CONFIGURACIÓN DE CONEXIONES
# -------------------------------------------------------------------

load_dotenv()

ORIGEN = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'database': os.getenv('DB_NAME')
}

DESTINO = {
    'user': os.getenv('SUPABASE_DB_USER'),
    'password': os.getenv('SUPABASE_DB_PASSWORD'),
    'host': os.getenv('SUPABASE_DB_HOST'),
    'port': os.getenv('SUPABASE_DB_PORT'),
    'database': os.getenv('SUPABASE_DB_NAME')
}

def make_engine(cfg: Dict) -> Engine:
    """Construye un engine SQLAlchemy con configuración mejorada."""
    uri = (
        f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    )
    return create_engine(uri, echo=False, pool_pre_ping=True) 

# -------------------------------------------------------------------
#  FUNCIONES PRINCIPALES
# -------------------------------------------------------------------

def get_ordered_tables(engine: Engine) -> List[str]:
    """
    Devuelve las tablas en orden de carga correcto (dimensiones primero).
    Usa convención de nombres: dim_* primero, fact_* al final.
    """
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    
    # Ordenar tablas: primero dimensiones, luego hechos
    dim_tables = [t for t in all_tables if t.startswith('dim_')]
    fact_tables = [t for t in all_tables if t.startswith('fact_')]
    other_tables = [t for t in all_tables if t not in dim_tables + fact_tables]
    
    return dim_tables + other_tables + fact_tables

def reflect_metadata(engine: Engine) -> MetaData:
    """Refleja metadata con verificación de conexión."""
    try:
        meta = MetaData()
        meta.reflect(bind=engine)
        return meta
    except SQLAlchemyError as e:
        print(f"❌ Error al reflejar metadata: {e}")
        raise

def recreate_schema(dest_engine: Engine, metadata: MetaData):
    """Recrea esquema con manejo de errores mejorado."""
    try:
        print("🔄 Recreando esquema en destino...")
        with dest_engine.begin() as conn:
            metadata.drop_all(conn, checkfirst=True)
            metadata.create_all(conn)
        print("✔ Esquema recreado exitosamente")
    except SQLAlchemyError as e:
        print(f"❌ Error al recrear esquema: {e}")
        raise

def copy_data(src_engine: Engine, dest_engine: Engine, metadata: MetaData):
    """Copia datos en el orden correcto con manejo transaccional."""
    ordered_tables = get_ordered_tables(src_engine)
    print(f"🔍 Orden de replicación: {ordered_tables}")
    
    SessionDest = sessionmaker(bind=dest_engine)
    sess_dest = SessionDest()
    
    try:
        with src_engine.connect() as src_conn:
            for table_name in ordered_tables:
                table_obj = metadata.tables[table_name]
                print(f"➡ Copiando datos de '{table_name}'...")
                
                try:
                    # Leer datos
                    result = src_conn.execute(select(table_obj))
                    rows = result.mappings().all()
                    
                    if not rows:
                        print(f"   ⚠ Tabla vacía, omitiendo")
                        continue
                        
                    # Insertar en destino
                    sess_dest.execute(table_obj.insert(), rows)
                    sess_dest.commit()
                    print(f"   ✔ {len(rows)} filas copiadas")
                    
                except SQLAlchemyError as e:
                    sess_dest.rollback()
                    print(f"   ❌ Error en '{table_name}': {e}")
                    raise
                    
    finally:
        sess_dest.close()

# -------------------------------------------------------------------
#  FUNCIÓN PRINCIPAL
# -------------------------------------------------------------------

def main():
    try:
        print("🚀 Iniciando replicación...")
        
        # 1) Crear engines con manejo de errores
        try:
            engine_origen = make_engine(ORIGEN)
            engine_destino = make_engine(DESTINO)
            
            # Test de conexiones - FORMA CORRECTA
            with engine_origen.connect() as test_conn:
                test_conn.execute(text("SELECT 1")).fetchone()
            print("✔ Conexión a ORIGEN establecida")
            
            with engine_destino.connect() as test_conn:
                test_conn.execute(text("SELECT 1")).fetchone()
            print("✔ Conexión a DESTINO establecida")
                
        except Exception as e:  # Capturamos Exception más general para diagnóstico
            print(f"❌ Error de conexión: {str(e)}")
            # Agregar información de diagnóstico
            print("\n🔍 Diagnóstico:")
            print(f"Origen: postgresql://{ORIGEN['user']}:****@{ORIGEN['host']}:{ORIGEN['port']}/{ORIGEN['database']}")
            print(f"Destino: postgresql://{DESTINO['user']}:****@{DESTINO['host']}:{DESTINO['port']}/{DESTINO['database']}")
            return

        # 2) Reflejar metadata
        meta_origen = reflect_metadata(engine_origen)
        
        # 3) Recrear esquema en destino
        recreate_schema(engine_destino, meta_origen)
        
        # 4) Copiar datos en orden controlado
        copy_data(engine_origen, engine_destino, meta_origen)
        
        print("\n🎉 Replicación completada exitosamente!")
        
    except Exception as e:
        print(f"\n🔥 Error crítico: {e}")
    finally:
        # Cerrar conexiones
        engine_origen.dispose()
        engine_destino.dispose()

if __name__ == '__main__':
    main()
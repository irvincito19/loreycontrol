from sqlalchemy import create_engine, text, inspect
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://loreydent:loreydent_pass@localhost/loreydent" # Pruebo localhost por si acaso
)

# Intentar conectar
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    inspector = inspect(engine)
    
    print(f"Conectado a la base de datos: {SQLALCHEMY_DATABASE_URL}")

    # Columnas a agregar
    migrations = [
        ("patients", "doctor_id", "INT NULL"),
        ("patients", "initial_budget", "FLOAT DEFAULT 0.0"),
        ("appointments", "treatment_details", "TEXT NULL"),
        ("appointments", "cost", "FLOAT DEFAULT 0.0"),
        ("appointments", "location", "VARCHAR(100) NULL"),
        ("availability", "location", "VARCHAR(100) NULL"),
        ("availability_overrides", "location", "VARCHAR(100) NULL"),
    ]

    with engine.connect() as conn:
        for table, column, col_type in migrations:
            columns = [c['name'] for c in inspector.get_columns(table)]
            if column not in columns:
                print(f"Agregando columna {column} a la tabla {table}...")
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                conn.commit()
            else:
                print(f"La columna {column} ya existe en {table}.")

    print("Migración completada exitosamente.")

except Exception as e:
    print(f"Error durante la migración: {e}")
    print("Nota: Si la base de datos está en un contenedor Docker, asegúrate de que el puerto 3306 esté expuesto o ejecuta este script dentro del contenedor.")

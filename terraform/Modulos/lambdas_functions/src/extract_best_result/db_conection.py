import psycopg2
import os

def connect_db():
    """
    Conecta a la base de datos RDS Gold usando las variables de entorno.
    """
    return psycopg2.connect(
        host=os.getenv("GOLD_DB_HOST"),
        dbname=os.getenv("GOLD_DB_NAME"),
        user=os.getenv("GOLD_DB_USER"),
        password=os.getenv("GOLD_DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )
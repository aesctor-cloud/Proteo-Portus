import psycopg2
import os

def connect_db():
    """
    Conecta a la base de datos RDS Gold usando las variables de entorno.
    """
    return psycopg2.connect(
        host=os.getenv("RDS_HOST"),
        dbname=os.getenv("RDS_DB"),
        user=os.getenv("RDS_USER"),
        password=os.getenv("RDS_PASSWORD"),
        port=os.getenv("RDS_PORT", 5432)
    )
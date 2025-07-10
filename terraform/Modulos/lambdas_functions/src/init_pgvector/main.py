import psycopg2
import os

def handler(event, context):
    conn = psycopg2.connect(
        host=os.environ['RDS_HOST'],
        dbname=os.environ['RDS_DB'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASSWORD'],
        port=5432
    )

    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.close()
    conn.close()

    return {"status": "pgvector habilitado"}

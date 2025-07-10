import os
import json
import boto3
import psycopg2
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# AWS clients
bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")  


BEDROCK_MODEL = "amazon.titan-embed-text-v2:0"



def create_gold_table(conn):
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gold_table (
                    project_id TEXT PRIMARY KEY,
                    name_project TEXT,
                    start_date DATE,
                    completion_date DATE,
                    country TEXT,
                    location TEXT,
                    client_name TEXT,
                    value_contract NUMERIC,
                    currency TEXT,
                    name_consultant TEXT,
                    description TEXT,
                    processing_timestamp TIMESTAMP,
                    normalization_timestamp TIMESTAMP,
                    source_record_id TEXT,
                    normalized_by_function TEXT,
                    embedding vector(1024)
                );

                
            ''')



def connect_db():
    return psycopg2.connect(
        host=os.environ['RDS_HOST'],
        port=os.environ['RDS_PORT'],
        dbname=os.environ['RDS_DB'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASSWORD']
    )

def generate_embedding(text):
    
    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text}).encode("utf-8"),
    )
    result = json.loads(response["body"].read())
    return result.get("embedding", [])

def handler(event, context):
    """
    Este handler:
    1. Extrae proyectos desde la base Silver (tabla: silver_table)
    2. Genera embeddings con Bedrock
    3. Inserta los resultados en la base Gold (tabla: gold_embeddings)
    """

    # 1. Conexiones
    conn = connect_db()
    create_gold_table(conn)

    try:
        with conn.cursor() as cur:
            resultados= []
            for id in event.get('ids', []):
                logger.info(f"Validando registro con ID: {id}")
                cur.execute(f"SELECT * FROM silver_table WHERE project_id = %s", (id,))
                row = cur.fetchall()  # Esto devuelve una lista de tuplas
                resultados.extend(row)
            columns = [desc[0] for desc in cur.description]
            

        with conn.cursor() as cur:
            for row in resultados:
                row_dict = dict(zip(columns, row))
                name = row_dict.get("name", "")
                description = row_dict.get("description", "")
                full_text = f"{name}. {name}. Proyecto titulado '{name}'. {description}"
                embedding = generate_embedding(full_text)

                # Preparar datos para insertar
                values = list(row) + [embedding]
                # Preparar la lista de columnas para el insert
                insert_columns = columns + ["embedding"]
                placeholders = ', '.join(['%s'] * len(insert_columns))
                insert_columns_str = ', '.join(insert_columns)

                # Construye el SQL dinamicamente
                sql = f"""
                    INSERT INTO gold_table ({insert_columns_str})
                    VALUES ({placeholders})
                    ON CONFLICT (project_id) DO UPDATE SET
                    {', '.join([f"{col} = EXCLUDED.{col}" for col in insert_columns if col != "project_id"])}
                """
                cur.execute(sql, values)

            conn.commit()

    finally:
        conn.close()
    
    logger.info(f"Resultados insertados en tabla oro: {resultados}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{len(resultados)} proyectos procesados."})
    }

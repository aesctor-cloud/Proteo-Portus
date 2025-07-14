import os
import json
import psycopg2
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_db_connection():
    return psycopg2.connect(
        host=os.environ['RDS_HOST'],
        port=os.environ['RDS_PORT'],
        dbname=os.environ['RDS_DB'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASSWORD']
    )

def insert_record(cursor, record):
    metadata = record[0]["metadata"]
    record = record[0]  # Assuming we are processing the first record in the list
    datos_sin_metadata = {}
    for clave, valor in record.items():
        if clave != "metadata":
            datos_sin_metadata[clave] = valor
    query = """
    INSERT INTO silver_table (
        project_id, name_project, start_date, completion_date,
        country, location, client_name, value_contract,
        currency, project_field, name_consultant, description, processing_timestamp,
        normalization_timestamp, source_record_id, normalized_by_function
    ) VALUES (
        %(project_id)s, %(name_project)s, %(start_date)s, %(completion_date)s,
        %(country)s, %(location)s, %(client_name)s, %(value_contract)s,
        %(currency)s, %(project_field)s, %(name_consultant)s, %(description)s, %(processing_timestamp)s,
        %(normalization_timestamp)s, %(source_record_id)s, %(normalized_by_function)s

    ) ON CONFLICT (project_id) DO UPDATE SET
    name_project = EXCLUDED.name_project,
    start_date = EXCLUDED.start_date,
    completion_date = EXCLUDED.completion_date,
    country = EXCLUDED.country,
    location = EXCLUDED.location,
    client_name = EXCLUDED.client_name,
    value_contract = EXCLUDED.value_contract,
    currency = EXCLUDED.currency,
    project_field = EXCLUDED.project_field,
    name_consultant = EXCLUDED.name_consultant,
    description = EXCLUDED.description,
    processing_timestamp = EXCLUDED.processing_timestamp,
    normalization_timestamp = EXCLUDED.normalization_timestamp,
    source_record_id = EXCLUDED.source_record_id,
    normalized_by_function = EXCLUDED.normalized_by_function;

    """
    values = {
        **record,
        "normalization_timestamp": metadata.get("normalization_timestamp"),
        "source_record_id": metadata.get("source_record_id"),
        "normalized_by_function": metadata.get("normalized_by_function"),

    }
    logger.info(f"Inserting record...: {values}")
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS silver_table (
                project_id TEXT PRIMARY KEY,
                name_project TEXT,
                start_date DATE,
                completion_date DATE,
                country TEXT,
                location TEXT,
                client_name TEXT,
                value_contract NUMERIC,
                currency TEXT,
                project_field TEXT,
                name_consultant TEXT,
                description TEXT,
                processing_timestamp TIMESTAMP,
                normalization_timestamp TIMESTAMP,
                source_record_id TEXT,
                normalized_by_function TEXT
            );

            
        ''')
    cursor.execute(query, values)
    logger.info("Record inserted successfully")

def handler(event, context):
    try:
        logger.info(f"Received event: {event}") 
        normalized = []
        count = 0
        conn = get_db_connection()
        cursor = conn.cursor()

        ids=[]
        for item in event:
            if "valid_result" in item and "normalized_records" in item["valid_result"]:
                normalized=item["valid_result"]["normalized_records"]
                insert_record(cursor, normalized)
                project_id=normalized[0].get("project_id")
                ids.append(project_id)
                count += 1
            
            
        conn.commit()
        cursor.close()
        conn.close()

        logger.info("Inserted %d records into the database", count)
        return {
            "ids": ids,
            "inserted": count,
            "message": "Records inserted successfully"
        }

    except Exception as e:
        logger.exception(f"Error inserting records: {e}")
        return {
            "error": str(e),
            "inserted": 0
        }

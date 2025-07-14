import boto3
import logging
import io
import json
import os
import pandas as pd
import time
from docx import Document
from openai import OpenAI
from typing import List, Dict, Any
import re
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import hashlib

# Load environment variables
load_dotenv()
# agent_id = os.getenv("BEDROCK_AGENT_ID")

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define the bronze columns structure
BRONZE_COLUMNS = [
    'project_id', 'name_project', 'start_date', 'completion_date',
    'country', 'location', 'client_name', 'project_field', 'value_contract',
    'currency', 'name_consultant', 'description'
]



def handler(event, context):
    start_time = time.time()
    try:
        logger.info("=== Lambda STARTED ===")

        
        bucket_name = event['detail']['bucket']['name']
        object_key = event['detail']['object']['key']

        logger.info(f"Archivo recibido: {object_key} en bucket: {bucket_name}")

        first_folder = object_key.split('/', 1)[0]
        logger.info(f"La primera carpeta es: {first_folder}")

        s3 = boto3.resource('s3')
        obj = s3.Object(bucket_name, object_key)

        t0 = time.time()
        extracted_text = extract_text_from_docx(obj)
        logger.info(f"Texto extraído en {time.time() - t0:.2f}s")

        processed_data = []

        if extracted_text:
            for i, table in enumerate(extracted_text):
                logger.info(f"Enviando tabla {i+1} a BedRock...")
                t_ai = time.time()
                analyzed_data = analyze_with_bedrock(table, object_key, first_folder)
                logger.info(f"BedRock procesó tabla {i+1} en {time.time() - t_ai:.2f}s")
                if analyzed_data:
                    processed_data.append(analyzed_data)

        if processed_data:
            t_db = time.time()
            conn = get_database_connection()
            logger.info("Conexión a RDS establecida")
            create_and_insert_table(conn, processed_data)
            logger.info(f"Datos insertados en {time.time() - t_db:.2f}s")
        else:
            logger.warning("No se generaron datos procesados para insertar")

        logger.info(f"=== Lambda TERMINÓ en {time.time() - start_time:.2f}s ===")
        data= {
            'statusCode': 200,
            'body': json.dumps({
                'data': 'Document processing completed successfully',
                # 'processed_data': processed_data
            })
        }

        ids= []
        for project in processed_data:
            project_id=project.get('project_id')
            ids.append(project_id)

        logger.info(f"Ids insertados: {ids}")
        logger.info(f"{data}")
        return {"ids": ids}
    
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def extract_text_from_docx(obj) -> list:
    try:
        logger.info("Obteniendo objeto desde S3...")
        body = obj.get()['Body'].read()
        logger.info("Objeto leído correctamente desde S3")

        if body == b'':
            logger.warning(f"Archivo vacío: {obj.key}")
            return []

        logger.info("Abriendo documento DOCX...")
        doc = Document(io.BytesIO(body))
        textos = []

        for table in doc.tables:
            filas = []
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    filas.append(" | ".join(row_text))
            if filas:
                textos.append('\n'.join(filas))

        logger.info(f"Se extrajeron {len(textos)} tablas del documento.")
        return textos

    except Exception as e:
        logger.error(f"Error extrayendo texto de {obj.key}: {str(e)}")
        return []


def analyze_with_bedrock(text: str, filename: str, first_folder: str) -> Dict[str, Any]:

    try:
        prompt = f"""
        TASK: Extract project information from the following text.

        Required columns: {', '.join(BRONZE_COLUMNS)}

        INPUT TEXT:
        {text}

        OUTPUT FORMAT: You must return EXACTLY this JSON structure with these exact field names:
    
        {{
            "name_project": "[PROJECT_NAME]",
            "start_date": "[YYYY-MM-DD or N/A]",
            "completion_date": "[YYYY-MM-DD or N/A]", 
            "country": "[ISO_ALPHA_3_CODE]",
            "location": "[LOCATION_IN_ENGLISH]",
            "client_name": "[CLIENT_NAME]",
            "value_contract": "[NUMBERS_ONLY]",
            "currency": "[ISO_4217_CODE]",
            "name_consultant": "[CONSULTANT_NAME]",
            "description": "[DESCRIPTION]"
        }}
        
        VALIDATION RULES:
        - location: City or place name in English, no additional formatting (e.g., "New York", "Madrid", "London")
        - country: Must be ISO 3166-1 alpha-3 (USA, ESP, FRA, DEU, etc.)
        - currency: Must be ISO 4217 (USD, EUR, GBP, etc.)
        - value_contract: Only digits, no symbols or letters
        - dates: YYYY-MM-DD format only
        - All fields mandatory, use "N/A" if not found
        - Response language: English only
        - No text outside JSON structure
        
        RESPONSE:
        """

        bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")  

        body = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.2
        }
        logger.info(f"Enviando solicitud a Bedrock...{body}")

        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )

        logger.info("Respuesta de Bedrock recibida")
        response_body = json.loads(response['body'].read())
        model_output = response_body['content'][0]['text'].strip()

        json_match = re.search(r'\{.*\}', model_output, re.DOTALL)
        if json_match:
            parsed_data = json.loads(json_match.group())
            parsed_data['project_field'] = first_folder
            parsed_data['project_id'] = generate_project_id(parsed_data)
            parsed_data['source_file'] = filename
            parsed_data['processing_timestamp'] = pd.Timestamp.now().isoformat()
            return parsed_data
        else:
            logger.warning(f"Respuesta inválida de Bedrock: {model_output}")
            return None

    except Exception as e:
        logger.error(f"Error en análisis con Bedrock: {str(e)}")
        return None


def get_database_connection():
    return psycopg2.connect(
        host=os.getenv("RDS_HOST"),
        port=os.getenv("RDS_PORT"),
        dbname=os.getenv("RDS_DB"),
        user=os.getenv("RDS_USER"),
        password=os.getenv("RDS_PASSWORD")
    )

def create_and_insert_table(conn, data):
    try:
        cursor = conn.cursor()
        logger.info("Verificando existencia de tabla bronze_table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bronze_table (
                project_id TEXT PRIMARY KEY,
                name_project TEXT,
                start_date TEXT,
                completion_date TEXT,
                country TEXT,
                location TEXT,
                client_name TEXT,
                value_contract TEXT,
                currency TEXT,
                project_field TEXT,
                name_consultant TEXT,
                description TEXT,
                source_file TEXT,
                processing_timestamp TIMESTAMP
            );
        ''')

        for row in data:
            columns = list(row.keys())
            values = list(row.values())
            logger.info(f"Inserting row: {row}")

            update_columns = [col for col in columns if col != "project_id"]
            update_str = ", ".join([f'{col} = EXCLUDED.{col}' for col in update_columns])

            cursor.execute(f"""
                INSERT INTO bronze_table ({', '.join(columns)})
                VALUES ({', '.join(['%s'] * len(values))})
                ON CONFLICT (project_id) DO UPDATE SET

                {update_str};
            """, 
            values
            )


        conn.commit()
        logger.info(f"{len(data)} filas insertadas en bronze_table")
    except Exception as e:
        logger.error(f"Error al insertar en DB: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def generate_project_id(project):
    relevant_data = {
        "name": project["name_project"],
        "start_date": project["start_date"],
        "completion_date": project["completion_date"],
    }
    
    
    string_data = json.dumps(relevant_data, sort_keys=True)

    # Usa SHA256 para generar un ID único pero repetible
    return hashlib.sha256(string_data.encode("utf-8")).hexdigest()

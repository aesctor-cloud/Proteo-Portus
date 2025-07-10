from validation import ProjectRaw
from pydantic import ValidationError
from database import get_database
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def handler(event, context):
    conn = get_database()
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    resultados = []
    for id in event.get('ids', []):
        logger.info(f"Validando registro con ID: {id}")
        cursor.execute(f"SELECT * FROM bronze_table WHERE project_id = %s", (id,))
        filas = cursor.fetchall()  # Esto devuelve una lista de dicts
        resultados.extend(filas)
    response = []
    for fila in resultados:
        try:
            record = ProjectRaw(**fila)
            record_dict = record.dict()
           
            record_dict["processing_timestamp"] = record_dict["processing_timestamp"].isoformat()
            response.append({"valid": True, "records": record_dict})
            logger.info(f"Registro válido: {record_dict}")
        except ValidationError as e:
            
            if isinstance(fila["processing_timestamp"], datetime):
                fila["processing_timestamp"] = fila["processing_timestamp"].isoformat()
            response.append({
                "valid": False,
                "records": fila,
                "errors": e.errors()
            })
            logger.error(f"Registro no válido: {fila}")
    return {"results": response}

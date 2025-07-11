import json
import logging
import unicodedata
from core.normalizer import normalize_record
from core.validator import is_valid_record
from config.field_mapping import get_default_field_mapping

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def normalize_unicode_and_strip(obj):
    """
    Normaliza unicode y limpia espacios en todos los valores str de un dict (recursivo).
    """
    if isinstance(obj, dict):
        return {k: normalize_unicode_and_strip(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_unicode_and_strip(x) for x in obj]
    elif isinstance(obj, str):
        return unicodedata.normalize("NFKC", obj).strip()
    else:
        return obj

def handler(event, context):
    """
    Lambda function para normalizar y transformar datos.
    
    Args:
        event: dict con:
            - 'records': Lista de diccionarios con los datos a procesar
            - 'config': (Opcional) Configuración de mapeo de campos
        context: Contexto de Lambda (no usado)
    
    Returns:
        dict: Respuesta con los datos normalizados o error. Si hay errores, incluye el registro y motivo.
    """
    try:
        # Validar entrada
        if 'records' not in event:

            logger.error('Missing records in event data')
            return {
                    'error': 'Missing records in event data',
                    'processed_count': 0,
                    'failed_count': 0
                }
        logger.info('Received event data: %s', event)
        record = event.get('records')
        logger.info(f"Received records: {record}")

        # Normalizar unicode y limpiar espacios en todos los valores de los registros
        record = normalize_unicode_and_strip(record)
        field_mapping = get_default_field_mapping()

        normalized_records = []

        try:
            
            normalized = normalize_record(record, field_mapping)
            logger.info(f"Normalized record: {normalized}")
            if is_valid_record(normalized):
                normalized_records.append(normalized)
            else:
                response = {
                        
                        'valid_transformation': False,
                        'processed_count': len(normalized_records),                   
                        'records': record,
                        'processed_count': len(normalized_records),
                        'failed_in': record,
                        'normalized_records': normalized_records,
                    }
                logger.error(f"Registro no válido por error previo: {response}")
                return record
            
        except Exception as e:
            logger.error(f"Error normalizando registro. Error {e}")
            response = {
                    'valid_transformation': False,
                    'records': record,
                    'processed_count': len(normalized_records),
                    'failed_in': record,
                    'normalized_records': normalized_records,
                }
           
            return response
              

        response = {
                'valid_transformation': True,
                'records': record,
                'processed_count': len(normalized_records),
                'normalized_records': normalized_records,
            }
        logger.info(f"Transformación exitosa: {response}")
        return response
    
    except Exception as e:
        logger.exception("Error interno en handler_transformation")
        return {
                'error': f'Internal processing error: {str(e)}',
                'processed_count': 0,
                'failed_count': 0
            }

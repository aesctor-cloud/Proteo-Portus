import json
import logging

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Lambda que registra cualquier evento recibido.
    """
    logger.info("=== Evento recibido ===")
    logger.info(json.dumps(event, indent=2))

    return {
        "status": "ok",
        "message": "Evento logueado correctamente"
    }

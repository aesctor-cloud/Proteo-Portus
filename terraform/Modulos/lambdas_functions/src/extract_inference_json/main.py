from models import FilterResult  # tu esquema Pydantic
import boto3
import json
import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context) -> dict:
    user_prompt = event.get("prompt", "")
    bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")  

    campos = """
    Los campos disponibles en la base de datos son:
    - name_project (texto, para embeddings)
    - description (texto, para embeddings)  
    - country (string, para embeddings)
    - location (string, para embeddings)
    - client_name (texto, para embeddings)
    - start_date (fecha ISO, para filtro - formato YYYY-MM-DD)
    - completion_date (fecha ISO, para filtro - formato YYYY-MM-DD)
    - project_field (string, para embeddings)
    - value_contract (float, para filtro)
    - currency (string, para embeddings)
    - name_consultant (texto, para embeddings)
    """

    prompt = f"""
    {campos}

    INSTRUCCIONES IMPORTANTES:
    1. Devuelve **únicamente un JSON válido**, sin explicaciones ni texto adicional.
    2. El JSON debe seguir este formato:
    {{
    "filters": [
        {{
        "field": "start_date",
        "operator": ">",
        "value": "2023-01-01"
        }},
        {{
        "field": "value_contract",
        "operator": "<",
        "value": 5000000
        }}
    ],
    "embedding_fields": "proyecto solar en Andalucía iniciado después de 2023"
    }}

    3. Usa 'filters' solo para campos numéricos (`value_contract`) o fechas (`start_date`, `completion_date`)
    4. Para fechas, convierte SIEMPRE a formato ISO 8601 (YYYY-MM-DD)
    5. Para texto, ubicaciones o conceptos generales, usa `embedding_fields`
    6. **No incluyas países como filtro**, van en `embedding_fields`

    Consulta del usuario:
    \"\"\"{user_prompt}\"\"\"

    Devuelve solo un JSON como este, sin texto adicional.
    """

    body = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.2
    }

    logger.info(f"Enviando solicitud a Bedrock con prompt: {user_prompt}")

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    response_body = json.loads(response['body'].read())
    model_output = response_body['content'][0]['text']
    logger.info(f"Raw model output: {model_output}")

    json_match = re.search(r'\{.*\}', model_output, re.DOTALL)

    if not json_match:
        logger.error("No se encontró JSON válido en la respuesta del modelo.")
        raise ValueError("La respuesta del modelo no contiene un JSON válido.")

    try:
        parsed_json = json.loads(json_match.group())
        result = FilterResult.model_validate(parsed_json)
        result_dict = result.model_dump()
        result_dict['prompt'] = user_prompt
        logger.info(f"Respuesta estructurada recibida: {result}")
        return result_dict
    except Exception as e:
        logger.exception("Error al parsear la respuesta del modelo.")
        raise ValueError(f"Error al validar el JSON: {str(e)}")

    
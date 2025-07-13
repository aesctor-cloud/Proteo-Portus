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
    Available database fields are:
    - project_field (string, for embeddings)
    - name_project (text, for embeddings)
    - start_date (ISO date, for filter - format YYYY-MM-DD)
    - completion_date (ISO date, for filter - format YYYY-MM-DD)
    - country (string, for embeddings)
    - location (string, for embeddings)
    - client_name (text, for embeddings)
    - value_contract (float, for filter)
    - currency (string, for embeddings)
    - name_consultant (text, for embeddings)
    - description (text, for embeddings)  
    """

    prompt = f"""
    TASK: Extract query parameters from the user's prompt to generate a JSON structure for database filtering and embedding search.

    Available fields and their types:
    {campos}

    INPUT USER PROMPT:
    {user_prompt}

    OUTPUT FORMAT: You must return EXACTLY this JSON structure with these exact field names:
    {{
        "filters": [
            {{
                "field": "[FIELD_NAME]",
                "operator": "[OPERATOR]",
                "value": "[VALUE]"
            }}
            // Add more filter objects if applicable
        ],
        "embedding_fields": "[TEXT_FOR_EMBEDDINGS]"
    }}
    
    VALIDATION RULES:
    - **filters**:
        - Only use for numeric fields (`value_contract`) or date fields (`start_date`, `completion_date`).
        - **Dates**: Must be in YYYY-MM-DD format only. If the year is not specified in the user prompt, use "N/A" for the filter value.
        - **Operators**: Use standard comparison operators (e.g., ">", "<", ">=", "<=", "=", "!=").
        - **Values**: For `value_contract`, only digits, no symbols or letters.
        - If no suitable filters are found, the `filters` array must be empty `[]`.
    - **embedding_fields**:
        - Use for textual descriptions, project names, countries, locations, client names, project fields, currencies, and consultant names.
        - **Do NOT include countries as filters**; they must go into `embedding_fields`.
        - If no relevant text for embeddings is found, use an empty string `""`.
    - **All fields mandatory**: The `filters` array and `embedding_fields` string must always be present in the JSON.
    - **Response language**: English only.
    - **No text outside JSON structure**.

    RESPONSE:
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

    
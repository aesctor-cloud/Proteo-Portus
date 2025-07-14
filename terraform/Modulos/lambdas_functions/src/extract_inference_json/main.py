from models import FilterResult  # tu esquema Pydantic
import boto3
import json
import re
import logging

from utils.country_utils import normalize_country
from utils.currency_utils import normalize_currency_code
from utils.number_utils import parse_value_input
from utils.date_utils import normalize_date_to_iso

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context) -> dict:
    user_prompt = event.get("prompt", "")
    bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")  

    campos = """
    Available database fields are:
    - project_field (string, for filters)
    - name_project (text, for embeddings)
    - start_date (ISO date, for filters - format YYYY-MM-DD)
    - completion_date (ISO date, for filters - format YYYY-MM-DD)
    - country (ISO 3166-1 alpha-3, for filters)
    - location (string, for embeddings)
    - client_name (text, for embeddings)
    - value_contract (float, for filters)
    - currency (ISO 4217, for filters)
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
        - Use only for the following fields:
            - Numeric fields: `value_contract`
            - Date fields: `start_date`, `completion_date`
            - ISO fields:
                - `country` (must be valid ISO 3166-1 alpha-3)
                - `currency` (must be valid ISO 4217)
            - Project field: `project_field`
                - Allowed values:
                    - `"energy"`
                    - `"transport_planning_and_mobility"`
                    - `"sustainability_and_environmental_assessment"`
                - If the project type can be inferred from the user prompt, include it as a filter.
                - If not enough context is provided to determine the type, do not include `project_field` in the filters.
        - **Dates**: Must be in YYYY-MM-DD format only. If the year is not specified in the user prompt, use `"N/A"` for the filter value.
        - **Operators**: Use standard comparison operators (e.g., ">", "<", ">=", "<=", "=", "!=").
        - **Values**:
            - `value_contract`: Only digits, no symbols or letters.
            - `country`: Only valid ISO 3166-1 alpha-3 codes (e.g., "ESP", "USA", "FRA").
            - `currency`: Only valid ISO 4217 codes (e.g., "EUR", "USD", "JPY").

        - If no suitable filters are found, the `filters` array must be empty `[]`.

    - **embedding_fields**:
        - Use for textual descriptions, project names, countries, locations, client names, project fields, currencies, and consultant names.
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

        # Normalizar los valores de los filtros
        normalized_filters = []
        allowed_project_fields = {"energy", "transport_planning_and_mobility", "sustainability_and_environmental_assessment"}
        for f in result_dict.get('filters', []):
            field = f.get('field')
            value = f.get('value')
            normalized_value = value
            if field == 'country':
                normalized_value = normalize_country(value)
            elif field == 'currency':
                normalized_value = normalize_currency_code(value)
            elif field == 'value_contract':
                normalized_value = parse_value_input(value)
            elif field in ('start_date', 'completion_date'):
                normalized_value = normalize_date_to_iso(value)
            elif field == 'project_field':
                normalized_value = value.strip().lower() if isinstance(value, str) else value
                if normalized_value not in allowed_project_fields:
                    normalized_value = None
            if normalized_value is not None:
                normalized_filters.append({**f, 'value': normalized_value})
        result_dict['filters'] = normalized_filters
        logger.info(f"Respuesta estructurada recibida: {result_dict}")
        return result_dict
    except Exception as e:
        logger.exception("Error al parsear la respuesta del modelo.")
        raise ValueError(f"Error al validar el JSON: {str(e)}")
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from typing import List, Union
import os
from dotenv import load_dotenv
import json
import boto3
import time
import uuid
from datetime import datetime


# Configura tu API Key de OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No se encontró OPENAI_API_KEY")

class SearchSessionManager:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('search-sessions')
    
    def generate_session_id(self):
        return str(uuid.uuid4())[:8]
    
    def save_search_context(self, session_id, filters, embedding_fields, offset=0):
        ttl = int(time.time()) + 3600  # 1 hora
        
        item = {
            'session_id': session_id,
            'filters': json.dumps(filters),
            'embedding_fields': embedding_fields,
            'last_offset': offset,
            'created_at': datetime.now().isoformat(),
            'ttl': ttl
        }
        
        self.table.put_item(Item=item)
    
    def get_search_context(self, session_id):
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            if 'Item' in response:
                item = response['Item']
                return {
                    'filters': json.loads(item['filters']),
                    'embedding_fields': item['embedding_fields'],
                    'last_offset': int(item['last_offset']),
                    'created_at': item['created_at']
                }
        except Exception as e:
            print(f"Error recuperando contexto: {e}")
        return None
    
    def update_offset(self, session_id, new_offset):
        self.table.update_item(
            Key={'session_id': session_id},
            UpdateExpression='SET last_offset = :offset',
            ExpressionAttributeValues={':offset': new_offset}
        )

def detect_continuation(prompt) -> bool:
    """Detecta si el prompt es una continuación usando LLM"""
    
    # Configura el modelo LangChain OpenAI
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=10)
    
    try:
        messages = [
            SystemMessage(content="Responde solo 'true' o 'false'. Determina si este mensaje solicita continuar o ampliar información de una conversación previa."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        result = response.content.strip().lower()
        return result == "true"
        
    except Exception:
        # Fallback a método regex si falla la API
        import re
        continuation_patterns = [
            r'\b(más|otros|siguientes|adicionales)\b',
            r'\b\d+\s+(más|otros|siguientes|adicionales)\b',
            r'\bmuestra\s+(más|otros)\b',
            r'\bcontinúa\b',
            r'\bsigue\b',
            r'\bpróximos?\b'
        ]
        
        prompt_lower = prompt.lower()
        return any(re.search(pattern, prompt_lower) for pattern in continuation_patterns)
    
# Función Lambda para extraer filtros y campos de embedding desde un prompt de usuario
def extract_json_handler(event, context) -> dict:
    """
    Función Lambda que recibe un evento con un prompt de usuario 
    y devuelve filtros y campos de embedding en un json estructurado.
    """

    try:
        # Parsear el evento
        if isinstance(event.get("body"), str):
            body = json.loads(event.get("body"))
        else:
            body = event.get("body", {})
        
        user_prompt = body.get("prompt", "")
        session_id = body.get("session_id", None)

        # Inicializar el manager de sesiones
        session_manager = SearchSessionManager()

        # Detectar si es continuación
        is_continuation = detect_continuation(user_prompt)

        if is_continuation and session_id:
            # Intentar recuperar contexto anterior
            search_context = session_manager.get_search_context(session_id)
            
            if search_context:
                # Es continuación válida - usar contexto anterior
                new_offset = search_context['last_offset'] + 50  # Ajusta según tu limit

                response_data = {
                    'is_continuation': True,
                    'session_id': session_id,
                    'filters': search_context['filters'],
                    'embedding_fields': search_context['embedding_fields'],
                    'offset': new_offset,
                    'message': 'Continuando búsqueda anterior'
                }

                return {
                    'statusCode': 200,
                    'body': response_data
                }
        
        # Nueva búsqueda
        # Definición de los modelos Pydantic para la salida estructurada
        class Filter(BaseModel):
            field: str
            operator: str
            value: Union[str, int, float]

        class FilterResult(BaseModel):
            filters: List[Filter]
            embedding_fields: str

        # Inicializa el modelo de lenguaje 
        llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
            api_key=api_key
        )

        # Configura el modelo para que devuelva una salida estructurada
        model_with_schema = llm.with_structured_output(schema=FilterResult)

        # Campos disponibles en la base de datos
        campos = """
        Los campos disponibles en la base de datos son:
        - project_name (texto, para embeddings)
        - project_description (texto, para embeddings)  
        - country (string, para embeddings)
        - start_date (fecha ISO, para filtro - formato YYYY-MM-DD)
        - end_date (fecha ISO, para filtro - formato YYYY-MM-DD)
        - year (número, para filtro)
        - project_type (string, para embeddings)
        - project_value (float, para filtro)
        """

        # Prompt para el modelo
        prompt = f"""
        {campos}

        INSTRUCCIONES IMPORTANTES:
        1. SOLO usa 'filters' para campos numéricos (year, project_value) y fechas (start_date, end_date)
        2. Para fechas, SIEMPRE convierte a formato ISO 8601 (YYYY-MM-DD). Ejemplos:
        - "1 de enero de 2023" → "2023-01-01"
        - "enero 2023" → "2023-01-01" (primer día del mes)
        - "2023" → usa el campo 'year' con valor numérico 2023
        - "antes de marzo 2024" → start_date < "2024-03-01"
        3. Para conceptos semánticos, texto descriptivo o ubicaciones, usa 'embedding_fields'
        4. Los embedding_fields deben ser una descripción en lenguaje natural
        5. No incluyas países como filtros, van en embedding_fields
        
        EJEMPLOS DE CONVERSIÓN DE FECHAS:
        - "iniciado el 15 de febrero de 2023" → start_date = "2023-02-15"
        - "terminado en diciembre 2022" → end_date = "2022-12-31"
        - "antes del 1 enero 2024" → start_date < "2024-01-01"
        - "después de junio 2023" → start_date > "2023-06-30"
        
        Consulta: "{user_prompt}"

        Analiza la consulta y extrae:
        1. filters: condiciones numéricas exactas y fechas en formato ISO
        2. embedding_fields: descripción natural para búsqueda semántica
        """

        # Invoca el modelo con el prompt
        response = model_with_schema.invoke(prompt)

        # Generar un nuevo session_id si es una nueva búsqueda
        new_session_id = session_manager.generate_new_session_id()

        # Convertir filters de Pydantic a dict
        filters_dict = [filter_item.model_dump() for filter_item in response.filters]

        # Guardar contexto de búsqueda
        session_manager.save_search_context(
            session_id=new_session_id,
            filters=filters_dict,
            embedding_fields=response.embedding_fields,
            offset=0
        )

        response_data = {
            'is_continuation': False,
            'session_id': new_session_id,
            'filters': filters_dict,
            'embedding_fields': response.embedding_fields,
            'offset': 0,
            'message': 'Nueva búsqueda iniciada'
        }

        # Devuelve la respuesta como un diccionario
        return {
            "statusCode": 200,
            "body": response_data
        }

    except Exception as e:
        # Manejo de errores
        return {
            "statusCode": 500,
            "body": {
                "error": str(e),
                "message": "Error procesando la solicitud"
            }
        }

if __name__ == "__main__":
    # Pruebas con diferentes consultas que incluyen fechas
    test_cases = [
        {
            "prompt": "Proyecto de energía solar en España iniciado en 1 de enero de 2023",
            "descripcion": "Fecha específica"
        },
        {
            "prompt": "Proyectos ecológicos terminados antes del 15 de marzo de 2024",
            "descripcion": "Fecha con operador 'antes'"
        },
        {
            "prompt": "Construcciones sostenibles iniciadas después de junio 2023 en Francia",
            "descripcion": "Fecha con operador 'después'"
        },
        {
            "prompt": "Proyectos de energía renovable del año 2022 con presupuesto mayor a 100000",
            "descripcion": "Año (no fecha específica)"
        },
        {
            "prompt": "Infraestructura verde iniciada entre enero y marzo de 2023 en Alemania",
            "descripcion": "Rango de fechas"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"PRUEBA {i}: {test_case['descripcion']}")
        print(f"Consulta: {test_case['prompt']}")
        print("-" * 60)
        
        result = extract_json_handler({"prompt": test_case["prompt"]}, None)
        body = result["body"]
        
        print("Filters:")
        for filter_item in body["filters"]:
            print(f"  - {filter_item['field']} {filter_item['operator']} {filter_item['value']}")
        
        print(f"Embedding fields: {body['embedding_fields']}")
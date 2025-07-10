from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import List, Union
import os
from dotenv import load_dotenv


# Configura tu API Key de OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No se encontró OPENAI_API_KEY")

# Función Lambda para extraer filtros y campos de embedding desde un prompt de usuario
def extract_json_handler(event, context) -> dict:

    user_prompt = event.get("prompt", "")

    # Definición de los modelos Pydantic para la salida estructurada
    class Filter(BaseModel):
        field: str
        operator: str
        value: Union[str, int, float]  # Removemos datetime, usaremos string para fechas ISO

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
    
    # Devuelve la respuesta como un diccionario
    return response.model_dump()

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
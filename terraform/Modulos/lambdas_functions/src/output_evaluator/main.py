import json
import boto3
import logging
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")

def format_projects(projects):
    lines = []
    for p in projects:
        # Genera formato que incluya nombre, código (si tiene), valor, fechas, actividades, etc.
        # Ajusta campos según tus datos reales:
        name_project = p.get("name_project", "Sin nombre")
        project_id = p.get("project_id", "N/A")
        description = p.get("description", "Sin descripción")
        value_contract = p.get("value_contract", "N/D")
        project_field = p.get("project_field", "N/D")
        dates = f"{p.get('start_date', 'N/D')} – {p.get('completion_date', 'N/D')}"
        currency = p.get("currency", "N/D")
        client_name = p.get("client_name", "N/D")
        country = p.get("country", "N/D")


        project_str = (
            f"[{name_project} ({project_id})]\n"
            f"● Presupuesto: {value_contract}\n"
            f"● Fechas: {dates}\n"
            f"● Moneda: {currency}\n"
            f"● Campo del proyecto: {project_field}\n"
            f"● Cliente: {client_name}\n"
            f"● País: {country}\n"
            f"● Descripción: {description}\n"
        )
        lines.append(project_str)
        formatted_project = "\n\n".join(lines)
        logger.info(f"Proyecto formateado: {formatted_project}")
    return formatted_project

def handler(event, context):
    try:
        # Extraer user_prompt y search_results directamente del evento
        user_prompt = event["search"]["Payload"]["user_prompt"]
        results = event["search"]["Payload"]["search_results"]

        if not user_prompt or not results:
            return {
                "error": True,
                "message": "Faltan 'user_prompt' o 'search_results' en el evento de entrada.",
                "details": "Input event missing required fields."
            }

        projects_formatted = format_projects(results)

        prompt = f"""
Eres un analista experto que recibe esta consulta de usuario y una lista de proyectos candidatos. 

Consulta del usuario:
"{user_prompt}"

Lista de proyectos (ya filtrados por fecha y presupuesto, no es necesario evaluar esos campos):

{projects_formatted}

RESPONDE SOLO con el resultado final, sin explicaciones intermedias ni razonamientos visibles. 

1. Para cada proyecto, provee un resumen detallado en el idioma de la consulta con un emoji (🟢/🟡/🔴) indicando si cumple con los requisitos.  
   Si la consulta incluye criterios específicos (ej. valor, fechas), estructura cada resultado así:

[PROYECTO (código referencia)]  
● Presupuesto: [monto]  
● Fechas: [inicio – fin]  
● Moneda: [moneda]  
● Cliente: [nombre]  
● País: [nombre]  
● Campo del proyecto: [nombre]  
● Descripción: [breve descripción del proyecto]
○ [lista con viñetas]  
🟢 / 🟡 / 🔴 Evaluación final con breve justificación.

Si la consulta tiene solo un requisito:  
[PROYECTO]  
● Requisitos: ✅/❌  
● Descripción breve.

2. Construye una tabla comparativa con:  
- Filas = proyectos  
- Columnas = requisitos clave inferidos de la consulta  
- Celdas:  
  - ✅ si el proyecto cumple al menos un 70% o más con el criterio  
  - ⚠️ si cumple entre un 30% y menos de 70%  
  - ❌ si cumple menos del 30%  
- Última columna "¿Cumple criterios?" con ✅, ⚠️ o ❌  

3. Antes de la tabla, asigna un score de relevancia cualitativo:  
🟢 Alta, 🟡 Moderada, 🔴 Baja

4. Ordena la tabla por relevancia (🟢 primero)

5. Finaliza con recomendaciones claras:  
- ✅ Mejores candidatos  
- ⚠️ Candidatos alternativos con justificación  
- ❌ Proyectos no recomendados

NO GENERES explicaciones ni pasos intermedios. Todo razonamiento debe quedar implícito en la respuesta.

RESPONDE SÓLO con el resultado final.

Proyectos:  
{json.dumps(results, ensure_ascii=False)}
"""
        body = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.2
        }

        response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
        )

        logger.info(f"Enviando solicitud a Bedrock con prompt: {prompt}")

        response_body = json.loads(response['body'].read())
        model_output = response_body['content'][0]['text']
        logger.info(f"Raw model output: {model_output}")

        # json_match = re.search(r'\{.*\}', model_output, re.DOTALL)
        

        # if not json_match:
        #     logger.error("No se encontró JSON válido en la respuesta del modelo.")
        #     raise ValueError("La respuesta del modelo no contiene un JSON válido.")

        try:
            # parsed_json = json.loads(json_match.group())
            logger.info(f"Respuesta estructurada recibida: {model_output}")
            return {
            "llm_response": model_output
        }
        except Exception as e:
            logger.exception("Error al parsear la respuesta del modelo.")
            raise ValueError(f"Error al validar el JSON: {str(e)}")

        
    except Exception as e:
        return {
            "error": True, 
            "message": "Error al generar la valoración de los proyectos.",
            "details": str(e)
        }
    
# if __name__ == "__main__":
    # test_event = {
    #     "body": json.dumps({
    #         "user_prompt": "Busco proyectos con actividades de instalación de paneles solares, duración mayor a 6 meses y cliente multinacional.",
    #         "top_projects": [
    #             {
    #                 "nombre": "Proyecto Sol A",
    #                 "codigo": "PSA001",
    #                 "valor": "5M USD",
    #                 "fecha_inicio": "2023-01-01",
    #                 "fecha_fin": "2023-12-31",
    #                 "proporcion": "100%",
    #                 "cliente": "SolarCorp",
    #                 "pais": "Chile",
    #                 "actividades": ["Instalación de paneles solares", "Mantenimiento"]
    #             },
    #             {
    #                 "nombre": "Proyecto Viento B",
    #                 "codigo": "PVB002",
    #                 "valor": "3M USD",
    #                 "fecha_inicio": "2023-03-01",
    #                 "fecha_fin": "2023-08-01",
    #                 "proporcion": "60%",
    #                 "cliente": "WindGlobal",
    #                 "pais": "Argentina",
    #                 "actividades": ["Construcción de torres eólicas", "Instalación de cableado"]
    #             }
    #         ]
    #     })
    # }

    # test_context = None

    # result = reason_projects_handler(test_event, test_context)
    # print(json.dumps(json.loads(result["body"]), ensure_ascii=False, indent=2))
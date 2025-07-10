import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def format_projects(projects):
    lines = []
    for p in projects:
        # Genera formato que incluya nombre, código (si tiene), valor, fechas, actividades, etc.
        # Ajusta campos según tus datos reales:
        name = p.get("nombre", "Sin nombre")
        ref = p.get("codigo", "N/A")
        value = p.get("valor", "N/D")
        dates = f"{p.get('start_date', 'N/D')} – {p.get('end_date', 'N/D')}"
        proportion = p.get("proporcion", "N/D")
        client = p.get("cliente", "N/D")
        country = p.get("pais", "N/D")
        activities = p.get("actividades", [])
        activities_str = "\n○ ".join(activities) if activities else "N/D"

        project_str = (
            f"[{name} ({ref})]\n"
            f"● Valor: {value}\n"
            f"● Fechas: {dates}\n"
            f"● Proporción: {proportion}\n"
            f"● Cliente: {client}\n"
            f"● País: {country}\n"
            f"● Actividades:\n○ {activities_str}"
        )
        lines.append(project_str)
    return "\n\n".join(lines)

def reason_projects_handler(event, context):
    try:
        # Extraer user_prompt y search_results directamente del evento
        user_prompt = event.get("user_prompt", "")
        projects = event.get("search_results", [])

        if not user_prompt or not projects:
            return {
                "error": True,
                "message": "Faltan 'user_prompt' o 'search_results' en el evento de entrada.",
                "details": "Input event missing required fields."
            }

        projects_formatted = format_projects(projects)

        prompt = f"""
Eres un analista experto que recibe esta consulta de usuario y una lista de proyectos candidatos. 

Consulta del usuario:
"{user_prompt}"

Lista de proyectos (ya filtrados por fecha y presupuesto, no es necesario evaluar esos campos):

{projects_formatted}

RESPONDE SOLO con el resultado final, sin explicaciones intermedias ni razonamientos visibles. 

1. Para cada proyecto, provee un resumen detallado en el idioma de la consulta con un emoji (🟢/🟡/🔴) indicando si cumple con los requisitos.  
   Si la consulta incluye criterios específicos (ej. valor, fechas, actividades), estructura cada resultado así:

[PROYECTO (código referencia)]  
● Valor: [monto]  
● Fechas: [inicio – fin]  
● Proporción: [proporción]  
● Cliente: [nombre]  
● País: [nombre]  
● Actividades:  
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
{json.dumps(projects, ensure_ascii=False)}
"""
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1200,
                "temperature": 0.5
            }),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']

        return {
            "llm_response": answer
        }

    except Exception as e:
        return {
            "error": True, 
            "message": "Error al generar la valoración de los proyectos.",
            "details": str(e)
        }
    
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "user_prompt": "Busco proyectos con actividades de instalación de paneles solares, duración mayor a 6 meses y cliente multinacional.",
            "top_projects": [
                {
                    "nombre": "Proyecto Sol A",
                    "codigo": "PSA001",
                    "valor": "5M USD",
                    "fecha_inicio": "2023-01-01",
                    "fecha_fin": "2023-12-31",
                    "proporcion": "100%",
                    "cliente": "SolarCorp",
                    "pais": "Chile",
                    "actividades": ["Instalación de paneles solares", "Mantenimiento"]
                },
                {
                    "nombre": "Proyecto Viento B",
                    "codigo": "PVB002",
                    "valor": "3M USD",
                    "fecha_inicio": "2023-03-01",
                    "fecha_fin": "2023-08-01",
                    "proporcion": "60%",
                    "cliente": "WindGlobal",
                    "pais": "Argentina",
                    "actividades": ["Construcción de torres eólicas", "Instalación de cableado"]
                }
            ]
        })
    }

    test_context = None

    result = reason_projects_handler(test_event, test_context)
    print(json.dumps(json.loads(result["body"]), ensure_ascii=False, indent=2))
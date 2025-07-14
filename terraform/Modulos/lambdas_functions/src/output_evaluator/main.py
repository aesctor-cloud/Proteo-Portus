import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")

def format_projects(projects):
    lines = []
    for p in projects:

        name_project = p.get("name_project", "Sin nombre")
        project_id = p.get("project_id", "N/A")
        value_contract = p.get("value_contract", "N/D")
        start_date = p.get("start_date", "N/D")
        completion_date = p.get("completion_date", "N/D")
        currency = p.get("currency", "N/D")
        project_field = p.get("project_field", "N/D")
        client_name = p.get("client_name", "N/D")
        country = p.get("country", "N/D")
        location = p.get("location", "N/D")
        description = p.get("description", "Sin descripción")
        name_consultant = p.get("name_consultant", "N/D")

        project_str = (
            f"[{name_project} ({project_id})]\n"
            f"● Presupuesto: {value_contract}\n"
            f"● Fechas: {start_date} – {completion_date}\n"
            f"● Moneda: {currency}\n"
            f"● Campo del proyecto: {project_field}\n"
            f"● Cliente: {client_name}\n"
            f"● País: {country}\n"
            f"● Ubicación: {location}\n"
            f"● Consultor: {name_consultant}\n"
            f"● Descripción: {description.strip()}\n"
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

        logger.info(f"Proyectos formateados: {projects_formatted}")

        logger.info(f"results: {json.dumps(results, ensure_ascii=False)}")

        prompt = f"""
        You are an expert project analyst. You receive:
        - The original user query describing desired project characteristics.
        - A list of filtered projects, preselected using structured filters and semantic embedding matching. Do NOT evaluate based on budget or date unless explicitly mentioned in the query.

        User query:
        "{user_prompt}"

        Candidate projects:
        {projects_formatted}

        INSTRUCTIONS – respond ONLY with the final output, no explanations or reasoning.

        1. For each project, provide a structured evaluation in the language of the user query, including:
        - A summary of the project.
        - A color emoji (🟢/🟡/🔴) reflecting overall fit to the query.
        - If the query includes specific requirements (budget, dates, country, etc.), format each project as:

        [PROJECT NAME (ref code)]  
        ● Budget: [float value]  
        ● Dates: [start – end]  
        ● Currency: [currency code]  
        ● Client: [client name]  
        ● Country: [country name]  
        ● Project Field: [field name]  
        ● Description: [brief summary]  
        ○ Key points as bullet list  
        🟢 / 🟡 / 🔴 Final evaluation with concise justification.

        If the query is broad or only includes general requirements:
        [PROJECT NAME]  
        ● Match: ✅ / ❌  
        ● Short summary.

        2. Create a comparison table:
        - Rows = Projects  
        - Columns = Key inferred criteria from the query  
        - Cell values:  
        - ✅ = strong match  
        - ⚠️ = not total match  
        - ❌ = poor/no match  
        - Final column: “Meets Criteria?” with ✅ / ⚠️ / ❌

        3. Before the table, assign a qualitative relevance score:
        🟢 High, 🟡 Moderate, 🔴 Low

        4. Sort the table by relevance score (🟢 first)

        5. End with recommendations:
        - ✅ Best candidates  
        - ⚠️ Posible candidates (with justification)  
        - ❌ Not recommended

        Do NOT generate intermediate steps or commentary. The reasoning must be embedded in your output structure.

        Projects JSON:
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
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
        )

        logger.info(f"Enviando solicitud a Bedrock con prompt: {prompt}")

        response_body = json.loads(response['body'].read())
        model_output = response_body['content'][0]['text']
        logger.info(f"Raw model output: {model_output}")

        try:
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
    
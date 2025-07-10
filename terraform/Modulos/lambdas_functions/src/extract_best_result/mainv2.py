import json
from db_conection import connect_db
from embedding_query import generate_embedding
from search import best_result_search, best_result_search_advanced
import boto3

class SearchSessionManager:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('search-sessions')
    
    def update_offset(self, session_id, new_offset):
        try:
            self.table.update_item(
                Key={'session_id': session_id},
                UpdateExpression='SET last_offset = :offset',
                ExpressionAttributeValues={':offset': new_offset}
            )
        except Exception as e:
            print(f"Error actualizando offset: {e}")

def search_projects_handler(event, context):
    """
    Lambda handler para buscar proyectos usando filtros SQL y embeddings semánticos
    """
    try:
        # Parsear el body del evento
        if isinstance(event.get("body"), str):
            body = json.loads(event.get("body"))
        else:
            body = event.get("body", {})

        # Extraer filtros y embedding fields de la primera lambda
        filters_list = body.get("filters", [])
        embedding_text = body.get("embedding_fields", None)
        session_id = body.get("session_id")
        offset = body.get("offset", 0)
        limit = body.get("limit", 50)  # Hacer configurable
        is_continuation = body.get("is_continuation", False)

        # Generar embedding si se proporciona texto
        embedding = None
        if embedding_text and embedding_text.strip():
            embedding = generate_embedding(embedding_text)  # Debe devolver una lista de floats

        # conectar a la base de datos
        conn = connect_db()
        try:
            with conn.cursor() as cur:
                """
                =============================================================================
                CONFIGURACIÓN DE BÚSQUEDA DE PROYECTOS
                =============================================================================

                Hay dos funciones disponibles para buscar proyectos:

                1. FUNCIÓN BÁSICA: best_result_search()
                - Búsqueda estándar con filtros SQL y/o embeddings
                - Parámetros: cursor, filters_list, embedding, limit
                - Uso recomendado: casos generales
                - Ejemplo:
                    best_results, columns = best_result_search(cur, filters_list, embedding, limit=50)

                2. FUNCIÓN AVANZADA: best_result_search_advanced()
                - Incluye threshold de similitud para embeddings
                - Mejor optimización para consultas híbridas (filtros + embeddings)
                - Parámetros adicionales: similarity_threshold (default: 0.7)
                - Uso recomendado: cuando necesites control fino sobre la similitud semántica
                - Ejemplo:
                    best_results, columns = best_result_search_advanced(
                        cur, filters_list, embedding, limit=50, similarity_threshold=0.6
                    )

                CAMBIAR AQUÍ LA FUNCIÓN A UTILIZAR:
                =============================================================================
                """

                # OPCIÓN 1: Función básica (por defecto)
                best_results, columns = best_result_search(cur, filters_list, embedding, 
                                                        offset=offset, limit=limit)

                # OPCIÓN 2: Función avanzada (descomenta para usar)
                # best_results, columns = best_result_search_advanced(
                #     cur, filters_list, embedding, offset=offset, limit=limit, similarity_threshold=0.7
                # )

                """
                =============================================================================
                NOTAS:
                - similarity_threshold: valores entre 0.0 y 1.0 (0.7 = 70% de similitud mínima)
                - limit: número máximo de resultados a devolver
                - Para búsquedas muy específicas, usa similarity_threshold más alto (0.8-0.9)
                - Para búsquedas más amplias, usa similarity_threshold más bajo (0.5-0.6)
                =============================================================================
                """

        finally:
            conn.close()

        # Actualizar offset en sesión si es continuación
        if is_continuation and session_id:
            session_manager = SearchSessionManager()
            session_manager.update_offset(session_id, offset)
        
        # Preparar los resultados finales
        response_data = {
            "results": best_results,
            "search_info": {
                "total_results": len(best_results),
                "offset": offset,
                "limit": limit,
                "filters_applied": len(filters_list),
                "semantic_search": embedding is not None,
                "session_id": session_id
            },
            "continuation_available": len(best_results) == limit,  # Si hay exactamente 'limit' resultados, probablemente hay más
            "context": {
                "is_continuation": is_continuation,
                "filters_used": filters_list,
                "embedding_query": embedding_text
            }
        }

        # Devuelve los resultados
        return {
            "statusCode": 200,
            "body": json.dumps(response_data, ensure_ascii=False, indent=2)
        }
    
    # Manejo de excepciones
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "message": "Error al procesar la solicitud de búsqueda"
            })
        }
    
if __name__ == "__main__":
    # Pruebas con diferentes filtros y embeddings
    test_cases = [
        {
            "filters": [{"field": "budget", "operator": ">", "value": 100000}],
            "embedding_fields": "Proyectos de energía solar en España"
        },
        {
            "filters": [{"field": "start_date", "operator": "<", "value": "2024-03-01"}],
            "embedding_fields": "Proyectos ecológicos"
        },
        {
            "filters": [{"field": "location", "operator": "=", "value": "Francia"}],
            "embedding_fields": "Construcciones sostenibles iniciadas después de junio 2023"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"PRUEBA {i}:")
        print(f"Filtros: {test_case['filters']}")
        print(f"Embedding Fields: {test_case['embedding_fields']}")
        print("-" * 60)
        
        result = search_projects_handler({"body": json.dumps(test_case)}, None)
        body = result["body"]
        
        print("Resultado:", body)
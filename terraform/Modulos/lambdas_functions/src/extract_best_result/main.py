import json
from db_conection import connect_db
from embedding_query import generate_embedding
from search import best_result_search, best_result_search_advanced
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Lambda handler para buscar proyectos usando filtros SQL y embeddings semánticos
    """
    try:
        # Extraer user_prompt, filtros y embedding fields
        user_prompt = event.get("prompt", "")
        filters_list = event.get("filters", [])
        embedding_text = event.get("embedding_fields", None)

        # Generar embedding si se proporciona texto
        embedding = None
 
        if embedding_text and embedding_text.strip():
            embedding = generate_embedding(embedding_text)  # Debe devolver una lista de floats
            logger.info(f"Embedding generado")

        # conectar a la base de datos
        conn = connect_db()
        logger.info("Conexión a la base de datos establecida")
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
                best_results, columns = best_result_search(cur, filters_list, embedding, limit=50)

                # OPCIÓN 2: Función avanzada (descomenta para usar) NO EN FUNCIONAMIENTO
                # best_results, columns = best_result_search_advanced(
                #     cur, filters_list, embedding, limit=50, similarity_threshold=0.7
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

        # Devuelve los resultados
        return {
            "user_prompt": user_prompt,
            "search_results": best_results,
            "total_results": len(best_results),
            "filters_applied": len(filters_list),
            "semantic_search_performed": embedding is not None,
        }
    
    # Manejo de excepciones
    except Exception as e:
        return {
            "error": True,
            "message": "Error al procesar la solicitud de búsqueda de proyectos.",
            "details": str(e)
        }
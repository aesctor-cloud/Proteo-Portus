import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def best_result_search(cursor, filters_list, embedding=None, limit=50):
    """
    Busca proyectos combinando filtros SQL y búsqueda semántica con pgvector
    
    Args:
        cursor: Cursor de la base de datos PostgreSQL
        filters_list: Lista de filtros SQL [{"field": "year", "operator": ">", "value": 2020}]
        embedding: Vector de embedding para búsqueda semántica (lista de floats)
        limit: Número máximo de resultados a devolver
    
    Returns:
        tuple: (resultados, nombres_columnas)
    """
    
    # Query base con todas las columnas necesarias
    # Si se quire extraer todas las columnas, *
    base_query = """
    SELECT 
        project_id,
        name_project,
        country,
        start_date,
        completion_date,
        project_field,
        value_contract,
        client_name,
        description
    """
    
    # Si hay embedding, agregar similitud coseno
    if embedding:
        # Convertir embedding a formato PostgreSQL array
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        
        base_query += f"""
        , (embedding <=> '{embedding_str}'::vector) as distance,
        (1 - (embedding <=> '{embedding_str}'::vector)) as similarity_score
        """
    
    # Agregar FROM tabla de proyectos (cambiar si se llama de otra forma)
    base_query += " FROM gold_table"
    
    # Construir condiciones WHERE para filtros SQL
    where_conditions = []
    params = []
    
    for filter_item in filters_list:
        field = filter_item.get("field")
        operator = filter_item.get("operator")
        value = filter_item.get("value")
        
        if field and operator and value is not None:
            # Mapear operadores seguros
            sql_operator_map = {
                "=": "=",
                ">": ">", 
                "<": "<",
                ">=": ">=",
                "<=": "<=",
                "!=": "!="
            }
            
            sql_operator = sql_operator_map.get(operator)
            if sql_operator:
                where_conditions.append(f"{field} {sql_operator} %s")
                params.append(value)
    
    # Agregar condiciones WHERE si existen filtros
    if where_conditions:
        base_query += " WHERE " + " AND ".join(where_conditions)
    
    # Ordenamiento y límite
    if embedding:
        # Si hay embedding, ordenar por similitud (menor distancia = mayor similitud)
        base_query += " ORDER BY embedding <=> %s"
        params.append(f"[{','.join(map(str, embedding))}]")
    else:
        # Sin embedding, ordenar por fecha más reciente
        base_query += " ORDER BY COALESCE(start_date, completion_date) DESC"

    base_query += f" LIMIT {limit}"
    
    try:
        logger.info(f"Ejecutando query: {base_query}")
        logger.info(f"Parámetros: {params}")
        
        # Ejecutar la consulta
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        # Obtener nombres de columnas
        columns = [desc[0] for desc in cursor.description]
        
        # Convertir resultados a formato más manejable
        formatted_results = []
        for row in results:
            project = dict(zip(columns, row))
            
            # Convertir tipos de datos para JSON
            for key, value in project.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    project[key] = value.isoformat()
                elif isinstance(value, (int, float, str, bool, type(None))):
                    continue  # Tipos JSON nativos
                else:
                    project[key] = str(value)  # Convertir otros tipos a string
            
            formatted_results.append(project)
        
        return formatted_results, columns
        
    except Exception as e:
        logger.info(f"Error en best_result_search: {str(e)}")
        raise e

def best_result_search_advanced(cursor, filters_list, embedding=None, limit=50, similarity_threshold=0.7):
    """
    Versión avanzada con threshold de similitud y mejor manejo de filtros
    """
    
    # Construir query más sofisticada
    if embedding and filters_list:
        # Caso híbrido: filtros + embeddings
        query = """
        WITH filtered_projects AS (
            SELECT *,
                   (1 - (embedding <=> %s::vector)) as similarity_score
            FROM gold_table
        """
        
        # Construir filtros
        where_conditions = []
        params = [f"[{','.join(map(str, embedding))}]"]  # Primer parámetro: embedding
        
        for filter_item in filters_list:
            field = filter_item.get("field")
            operator = filter_item.get("operator")
            value = filter_item.get("value")
            
            if field and operator and value is not None:
                sql_operator_map = {
                    "=": "=", ">": ">", "<": "<", 
                    ">=": ">=", "<=": "<=", "!=": "!="
                }
                
                sql_operator = sql_operator_map.get(operator)
                if sql_operator:
                    where_conditions.append(f"{field} {sql_operator} %s")
                    params.append(value)
        
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
            logger.info(f"querys filtros: {query}")
        
        query += f"""
        )
        SELECT 
            project_id, name_project, description, country,
            start_date, completion_date, project_field, value_contract, client_name,
            currency, 
            similarity_score
        FROM gold_table
        WHERE similarity_score >= {similarity_threshold}
        ORDER BY similarity_score DESC
        LIMIT {limit}
        """
        logger.info(f"Query avanzada: {query}")
    elif embedding:
        # Solo embeddings
        query = f"""
        SELECT 
            project_id, name_project, description, country,
            start_date, completion_date, project_field, value_contract, client_name,
            (1 - (embedding <=> %s::vector)) as similarity_score
        FROM gold_table
        WHERE (1 - (embedding <=> %s::vector)) >= {similarity_threshold}
        ORDER BY embedding <=> %s::vector
        LIMIT {limit}
        """
        embedding_str = f"[{','.join(map(str, embedding))}]"
        params = [embedding_str, embedding_str, embedding_str]

        logger.info(f"Query embeddings: {query}")
    elif filters_list:
        # Solo filtros SQL
        query = """
        SELECT 
            project_id, name_project, description, country,
            start_date, completion_date, project_field, value_contract, client_name
        FROM gold_table
        """
        
        where_conditions = []
        params = []
        
        for filter_item in filters_list:
            field = filter_item.get("field")
            operator = filter_item.get("operator") 
            value = filter_item.get("value")
            
            if field and operator and value is not None:
                sql_operator_map = {
                    "=": "=", ">": ">", "<": "<",
                    ">=": ">=", "<=": "<=", "!=": "!="
                }
                
                sql_operator = sql_operator_map.get(operator)
                if sql_operator:
                    where_conditions.append(f"{field} {sql_operator} %s")
                    params.append(value)
        
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        
        query += f" ORDER BY COALESCE(start_date, completion_date) DESC LIMIT {limit}"
        
        logger.info(f"Query filtros: {query}")
    else:
        # Sin filtros ni embeddings - devolver proyectos más recientes
        query = f"""
        SELECT 
            project_id, name_project, description, country,
            start_date, completion_date, value_contract, client_name
        FROM gold_table
        ORDER BY COALESCE(start_date, completion_date) DESC
        LIMIT {limit}
        """
        params = []
    
    try:
        logger.info(f"Query avanzada: {query}")
        logger.info(f"Parámetros: {params}")
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Formatear resultados
        formatted_results = []
        for row in results:
            project = dict(zip(columns, row))
            
            # Convertir tipos para JSON
            for key, value in project.items():
                if hasattr(value, 'isoformat'):
                    project[key] = value.isoformat()
                elif isinstance(value, (int, float, str, bool, type(None))):
                    continue
                else:
                    project[key] = str(value)
            
            formatted_results.append(project)
        
        return formatted_results, columns
        
    except Exception as e:
        logger.error(f"Error en best_result_search_advanced: {str(e)}")
        raise e

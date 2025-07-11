def best_result_search(cursor, filters_list=None, embedding=None, offset=0, limit=50, similarity_threshold=None):
    """
    Busca proyectos combinando filtros SQL y búsqueda semántica con pgvector
    
    Args:
        cursor: Cursor de la base de datos PostgreSQL
        filters_list: Lista de filtros SQL [{"field": "year", "operator": ">", "value": 2020}]
        embedding: Vector de embedding para búsqueda semántica (lista de floats)
        offset: Desplazamiento para paginación
        limit: Número máximo de resultados a devolver
        similarity_threshold: Umbral mínimo de similitud (0.0-1.0), solo para embeddings
    
    Returns:
        tuple: (resultados, nombres_columnas, metadata)
    """
    
    # Validación de entrada
    if filters_list is None:
        filters_list = []
    
    if limit <= 0 or limit > 1000:  # Limitar queries muy grandes
        limit = 50
    
    if offset < 0:
        offset = 0
    
    # Campos base de la consulta
    base_fields = [
        'project_id',
        'project_name', 
        'project_description',
        'country',
        'start_date',
        'end_date',
        'year',
        'project_type',
        'project_value'
    ]
    
    # Query base
    base_query = f"SELECT {', '.join(base_fields)}"
    
    # Parámetros para la consulta
    params = []
    
    # Si hay embedding, agregar campos de similitud
    if embedding and len(embedding) > 0:
        # Validar que el embedding sea una lista de números
        try:
            embedding = [float(x) for x in embedding]
        except (TypeError, ValueError):
            raise ValueError("El embedding debe ser una lista de números")
        
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        
        base_query += f"""
        , (embedding_vector <=> %s::vector) as distance,
        (1 - (embedding_vector <=> %s::vector)) as similarity_score
        """
        params.extend([embedding_str, embedding_str])
    
    # FROM clause
    base_query += " FROM projects"
    
    # Construir condiciones WHERE
    where_conditions = []
    
    # Procesar filtros SQL
    for filter_item in filters_list:
        if not isinstance(filter_item, dict):
            continue
            
        field = filter_item.get("field", "").strip()
        operator = filter_item.get("operator", "").strip()
        value = filter_item.get("value")
        
        if not field or not operator or value is None:
            continue
        
        # Validar campo (prevenir SQL injection)
        allowed_fields = {
            'project_id', 'project_name', 'project_description', 'country',
            'start_date', 'end_date', 'year', 'project_type', 'project_value'
        }
        
        if field not in allowed_fields:
            continue
        
        # Mapear operadores seguros
        sql_operator_map = {
            "=": "=", "eq": "=",
            ">": ">", "gt": ">",
            "<": "<", "lt": "<", 
            ">=": ">=", "gte": ">=",
            "<=": "<=", "lte": "<=",
            "!=": "!=", "ne": "!=", "<>": "!=",
            "like": "LIKE", "ilike": "ILIKE",
            "in": "IN", "not_in": "NOT IN"
        }
        
        sql_operator = sql_operator_map.get(operator.lower())
        if not sql_operator:
            continue
        
        # Manejar diferentes tipos de operadores
        if operator.lower() in ["in", "not_in"]:
            if isinstance(value, (list, tuple)) and len(value) > 0:
                placeholders = ",".join(["%s"] * len(value))
                where_conditions.append(f"{field} {sql_operator} ({placeholders})")
                params.extend(value)
        elif operator.lower() in ["like", "ilike"]:
            where_conditions.append(f"{field} {sql_operator} %s")
            params.append(value)
        else:
            where_conditions.append(f"{field} {sql_operator} %s")
            params.append(value)
    
    # Agregar filtro de similitud si se especifica threshold
    if embedding and similarity_threshold is not None:
        if 0.0 <= similarity_threshold <= 1.0:
            distance_threshold = 1.0 - similarity_threshold
            where_conditions.append("(embedding_vector <=> %s::vector) <= %s")
            params.extend([embedding_str, distance_threshold])
    
    # Agregar WHERE clause si hay condiciones
    if where_conditions:
        base_query += " WHERE " + " AND ".join(where_conditions)
    
    # ORDER BY clause
    if embedding:
        # Ordenar por similitud (menor distancia = mayor similitud)
        base_query += " ORDER BY embedding_vector <=> %s::vector"
        params.append(embedding_str)
    else:
        # Sin embedding, ordenar por fecha más reciente
        base_query += " ORDER BY COALESCE(start_date, end_date, (year || '-01-01')::date) DESC"
    
    # LIMIT y OFFSET
    base_query += f" OFFSET {offset} LIMIT {limit}"
    
    try:
        print(f"Ejecutando query: {base_query}")
        print(f"Número de parámetros: {len(params)}")
        
        # Ejecutar la consulta
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        # Obtener nombres de columnas
        columns = [desc[0] for desc in cursor.description]
        
        # Convertir resultados a formato JSON-serializable
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
        
        # Metadata adicional
        metadata = {
            "query_executed": True,
            "total_returned": len(formatted_results),
            "offset_used": offset,
            "limit_used": limit,
            "has_embedding": embedding is not None,
            "similarity_threshold": similarity_threshold,
            "filters_applied": len([f for f in filters_list if isinstance(f, dict) and f.get("field")])
        }
        
        return formatted_results, columns, metadata
        
    except Exception as e:
        print(f"Error en best_result_search: {str(e)}")
        print(f"Query que falló: {base_query}")
        print(f"Parámetros: {params}")
        raise e
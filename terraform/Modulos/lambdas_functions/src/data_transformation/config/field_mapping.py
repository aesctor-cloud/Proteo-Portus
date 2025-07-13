from typing import Dict, List

def get_default_field_mapping() -> Dict[str, List[str]]:
    """
    Devuelve el mapeo de campos por defecto.
    
    Returns:
        dict: Mapeo por defecto de campos
    """
    return {
        "project_id": ["id", "record_id", "project_id"],
        "name_project": ["name", "projectName", "nombreProyecto"],
        "country": ["country", "pais"],
        "start_date": ["startDate", "start_date", "date_start"],
        "completion_date": ["endDate", "end_date", "completion_date"],
        "currency": ["currency", "moneda"],
        "client_name": ["client", "client_name"],
        "project_field": ["project_field", "field", "area"],
        "location": ["location", "ubicacion", "lugar"],
        "value_contract": ["value_contract", "valorProyecto", "value"],
        "description": ["description", "descripcion", "details"],
        "name_consultant": ["name_consultant", "consultant", "asesor"],
        "processing_timestamp": ["processing_timestamp", "timestamp", "fecha_procesamiento"],
    }
from utils.country_utils import normalize_country
from utils.date_utils import normalize_date_to_iso
from utils.currency_utils import normalize_currency_code
from utils.text_utils import clean_and_capitalize_name, remove_unnecessary_newlines
from utils.number_utils import parse_value_input
from datetime import datetime
import datetime
    
def normalize_record(record, field_mapping):
    """
    Normaliza un registro individual aplicando las funciones de normalización.
    Los campos sin valor se mantienen como están en el registro original.

    Args:
        record (dict): Registro a normalizar
        field_mapping (dict): Mapeo de campos

    Returns:
        dict: Registro normalizado
    """
    normalized = record.copy()  # Start with a copy of the original record

    # --- Metadatos ---
    normalized['metadata'] = {
        'normalization_timestamp': datetime.datetime.now().isoformat(), # This now works!
        'source_record_id': record.get('id', 'N/A'),
        'normalized_by_function': 'normalize_record',
        'original_keys_present': list(record.keys())
    }

    # Helper function to apply normalization if value exists, otherwise keep original
    def apply_normalization(field_key, normalization_func):
        field_value = find_field_value(record, field_mapping.get(field_key, []))
        if field_value:
            normalized[field_key] = normalization_func(field_value)
        # If field_value is empty, it remains as it was in the original 'normalized' dict (which is a copy of 'record')

    # Normalize country
    apply_normalization('country', normalize_country)

    # Normalize date fields
    apply_normalization('start_date', normalize_date_to_iso)
    apply_normalization('completion_date', normalize_date_to_iso)
    apply_normalization('processing_timestamp', normalize_date_to_iso)

    # Normalize currency
    apply_normalization('currency', normalize_currency_code) # Note: If you want 'currency_code', adjust this.

    # Normalize company names
    apply_normalization('client_name', clean_and_capitalize_name)
    apply_normalization('name_consultant', clean_and_capitalize_name)
    apply_normalization('name_project', clean_and_capitalize_name)
    apply_normalization('location', clean_and_capitalize_name)
    apply_normalization('project_field', clean_and_capitalize_name)

    # Normalize numerical values
    apply_normalization('value_contract', parse_value_input)

    # Normalize text fields
    apply_normalization('description', remove_unnecessary_newlines)


    return normalized


def find_field_value(record, possible_fields):
    """
    Busca un valor en el registro usando una lista de posibles nombres de campo.
    
    Args:
        record (dict): Registro donde buscar
        possible_fields (list): Lista de posibles nombres de campo
    
    Returns:
        any: Valor encontrado o None
    """
    for field in possible_fields:
        if field in record and record[field] is not None:
            return record[field]
    return None

def get_all_mapped_fields(field_mapping):
    """
    Obtiene todos los campos que están mapeados.
    
    Args:
        field_mapping (dict): Mapeo de campos
    
    Returns:
        set: Conjunto de todos los campos mapeados
    """
    all_fields = set()
    for field_list in field_mapping.values():
        all_fields.update(field_list)
    return all_fields
from datetime import date, datetime
from dateutil.parser import parse, ParserError

def normalize_date_to_iso(date_input):
    """
    Normaliza una entrada de fecha (str, datetime, date) a su representación ISO 8601 (YYYY-MM-DD).
    Utiliza dateutil.parser para un parseo robusto de múltiples formatos de cadena.

    Args:
        date_input: La fecha a normalizar. Puede ser una cadena en varios formatos,
                    un objeto datetime.date, datetime.datetime, o incluso None.

    Returns:
        str or None: La fecha en formato ISO (YYYY-MM-DD) si la conversión es exitosa,
                     None en caso contrario (incluyendo entradas nulas o inválidas).
    """
    if date_input is None:
        return None

    # Si ya es un objeto datetime.date o datetime.datetime, convertir directamente a ISO
    if isinstance(date_input, (date, datetime)):
        return date_input.isoformat().split('T')[0] # Solo la parte de la fecha

    # Si es una cadena, intentar parsear con dateutil.parser
    if isinstance(date_input, str):
        try:
            # Eliminar espacios en blanco alrededor y verificar si la cadena está vacía
            cleaned_input = date_input.strip()
            if not cleaned_input:
                return None

            # dateutil.parser.parse() es muy flexible y puede inferir el formato
            dt_obj = parse(cleaned_input)
            return dt_obj.isoformat().split('T')[0] # Devolver solo la parte de la fecha
        except ParserError:
            # Error específico de dateutil.parser cuando no puede parsear
            return None
        except ValueError:
            # Otros errores de valor que podrían surgir (ej. fecha imposible)
            return None
        except Exception:
            # Capturar cualquier otra excepción inesperada
            return None
    
    # Si la entrada no es un tipo esperado, devolver None
    return None
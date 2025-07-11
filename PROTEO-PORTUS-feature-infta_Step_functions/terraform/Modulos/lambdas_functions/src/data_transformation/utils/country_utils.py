import pycountry

def normalize_country(country):
    """
    Primero verifica si la entrada es un código ISO 3166-1 alpha-3 válido.
    Si no lo es, intenta normalizar un nombre de país a su código ISO 3166-1 alpha-3.
    Solo soporta paises en ingles.

    Args:
        country_input (str): El nombre o código del país (ej., "ESP", "Spain", "México").

    Returns:
        str or None: El código ISO 3166-1 alpha-3 normalizado si se encuentra,
                     None en caso contrario.
    """

    # 0. Validar la entrada para evitar TypeError
    if not isinstance(country, str):
        return None
    
    country = country.strip()

    if not country:
        return None
    # 1. Intenta validar si ya es un código ISO 3166-1 alpha-3 válido
    try:
        # Convertir a mayúsculas y buscar por código
        upper_input = country.upper()
        country_by_code = pycountry.countries.get(alpha_3=upper_input)
        if country_by_code:
            return country_by_code.alpha_3
    except KeyError:
        # Si no se encuentra por código, intentar buscar por nombre
        pass
    except Exception:
        return None

    # 2. Si no se encuentra por código, intentar buscar por nombre del país
    try:
        found_countries = pycountry.countries.search_fuzzy(country)
        if found_countries:
            return found_countries[0].alpha_3
        return None # No se encontró el país
    except Exception:
        return None # Error en la búsqueda
    

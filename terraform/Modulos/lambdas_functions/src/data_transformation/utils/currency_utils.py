import pycountry

def normalize_currency_code(currency_input):
    """
    Normaliza una entrada de código de moneda a su formato estándar ISO 4217 (tres letras en mayúsculas).
    También valida si el código de moneda es reconocido.

    Args:
        currency_input (str): El código de moneda a normalizar (ej., "usd", "eur", "MXN").

    Returns:
        str or None: El código de moneda normalizado (ej., "USD") si es válido y reconocido,
                     None en caso contrario.
    """
    if not isinstance(currency_input, str):
        return None # Solo procesa strings

    # Convertir a mayúsculas para la validación y normalización
    upper_currency_code = currency_input.strip().upper()

    try:
        # Intentar obtener la moneda por su código ISO 4217 (alpha_3)
        # Esto valida si el código existe en la base de datos de pycountry
        currency = pycountry.currencies.get(alpha_3=upper_currency_code)
        
        # Si se encuentra, el código ya está en el formato deseado (mayúsculas) y es un código ISO válido.
        if currency:
            return upper_currency_code
        else:
            return None # Esto no debería ocurrir si get() no lanza KeyError, pero es un seguro
    except KeyError:
        # El código no fue encontrado en la base de datos ISO 4217
        return None
    except Exception:
        # Capturar cualquier otra excepción inesperada
        return None

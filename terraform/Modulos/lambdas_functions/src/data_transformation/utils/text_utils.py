import re
import pandas as pd
import unicodedata

def clean_and_capitalize_name(name_input):
    """
    Capitaliza la primera letra de cada palabra en nombres de personas, empresas y organizaciones.
    Limpia abreviaturas comunes y maneja preposiciones/conjunciones con casos especiales mejorados.

    Args:
        name_input (str): El nombre/empresa/organización a limpiar y capitalizar.

    Returns:
        str or None: El nombre limpio y capitalizado, o None si la entrada es nula o no es una cadena.
    """
    # Verificar si la entrada es válida
    if not name_input or not isinstance(name_input, str):
        return None
    
    # Limpiar espacios extra y convertir a minúsculas
    name = name_input.strip().lower()
    
    # Si después de limpiar queda vacío, retornar None
    if not name:
        return None
    
    # Diccionario de abreviaturas comunes y sus formas completas
    abbreviations = {
        # Títulos personales
        'mr.': 'Mr.',
        'mrs.': 'Mrs.',
        'ms.': 'Ms.',
        'dr.': 'Dr.',
        'prof.': 'Prof.',
        'sr.': 'Sr.',
        'sra.': 'Sra.',
        'srta.': 'Srta.',
        'dra.': 'Dra.',
        'lic.': 'Lic.',
        'ing.': 'Ing.',
        'arq.': 'Arq.',
        'mtro.': 'Mtro.',
        'mtra.': 'Mtra.',
        'jr.': 'Jr.',
        'sr': 'Sr.',
        'ii': 'II',
        'iii': 'III',
        'iv': 'IV',
        'v': 'V',
        # Términos empresariales
        'ltd.': 'Ltd.',
        'inc.': 'Inc.',
        'corp.': 'Corp.',
        'llc.': 'LLC.',
        'co.': 'Co.',
        'cia.': 'Cia.',
        'ltda.': 'Ltda.',
        'srl.': 'SRL.',
        'sa.': 'SA.',
        'sas.': 'SAS.',
        'sl.': 'SL.',
        'spa.': 'SpA.',
        'plc.': 'PLC.',
        'gmbh.': 'GmbH.',
        'ag.': 'AG.',
        'bv.': 'BV.',
        'nv.': 'NV.',
        'oy.': 'OY.',
        'ab.': 'AB.',
        'as.': 'AS.',
        'kft.': 'Kft.',
        'rt.': 'Rt.',
        'ltd': 'Ltd',
        'inc': 'Inc',
        'corp': 'Corp',
        'llc': 'LLC',
        'co': 'Co',
        'cia': 'Cia',
        'ltda': 'Ltda',
        'srl': 'SRL',
        'sa': 'SA',
        'sas': 'SAS',
        'sl': 'SL',
        'spa': 'SpA',
        'plc': 'PLC',
        'gmbh': 'GmbH',
        'ag': 'AG',
        'bv': 'BV',
        'nv': 'NV'
    }
    
    # Preposiciones y conjunciones que deben ir en minúsculas (excepto al inicio)
    lowercase_words = {
        # Español
        'de', 'del', 'la', 'las', 'los', 'el', 'y', 'e', 'o', 'u',
        'da', 'das', 'do', 'dos', 'di', 'le', 'les', 'van', 'von',
        'para', 'por', 'con', 'sin', 'sobre', 'bajo', 'entre', 'desde',
        'hacia', 'hasta', 'contra', 'según', 'durante', 'mediante',
        # Inglés
        'of', 'and', 'the', 'in', 'on', 'at', 'to', 'for', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among',
        'a', 'an', 'as', 'but', 'or', 'nor', 'so', 'yet',
        # Otras partículas comunes
        'af', 'al', 'ap', 'auf', 'aus', 'ben', 'bin', 'da', 'dal',
        'dalla', 'dalle', 'dello', 'der', 'des', 'di', 'du', 'ibn',
        'im', 'in', 'zu', 'zum', 'zur', 'op', 'ter', 'van', 'ver',
        'vom', 'von', 'zu'
    }
    
    # Palabras que siempre van en mayúsculas (acrónimos comunes)
    uppercase_words = {
        'usa', 'uk', 'eu', 'usd', 'eur', 'gbp', 'ceo', 'cfo', 'cto',
        'coo', 'hr', 'it', 'ai', 'ml', 'iot', 'api', 'ui', 'ux',
        'seo', 'crm', 'erp', 'b2b', 'b2c', 'roi', 'kpi', 'r&d',
        'p&l', 'rrhh', 'tic', 'pyme', 'mipyme', 'ong', 'ngo',
        'isbn', 'issn', 'iso', 'ieee', 'html', 'css', 'js', 'sql',
        'xml', 'json', 'http', 'https', 'ftp', 'ssh', 'vpn', 'lan',
        'wan', 'wifi', 'gps', 'usb', 'hdd', 'ssd', 'ram', 'cpu',
        'gpu', 'led', 'lcd', 'oled', 'hdmi', 'dvd', 'cd', 'mp3',
        'mp4', 'pdf', 'zip', 'rar', 'png', 'jpg', 'jpeg', 'gif',
        'svg', 'tiff', 'bmp', 'psd', 'ai', 'eps', 'dxf', 'dwg'
    }
    
    # Casos especiales para nombres con apóstrofes
    apostrophe_rules = {
        "o'": "O'",  # O'Connor, O'Brien
        "d'": "D'",  # D'Angelo, D'Amico
        "l'": "L'",  # L'Heureux
        "mc": "Mc",  # McDonald, McPherson
        "mac": "Mac" # MacDonald, MacPherson
    }
    
    # Dividir en palabras
    words = name.split()
    result_words = []
    
    for i, word in enumerate(words):
        # Verificar si debe ir en mayúsculas (acrónimos)
        if word in uppercase_words:
            result_words.append(word.upper())
            continue
        
        # Verificar abreviaturas
        if word in abbreviations:
            result_words.append(abbreviations[word])
            continue
        
        # Manejar casos especiales con apóstrofes
        if "'" in word:
            parts = word.split("'")
            if len(parts) == 2:
                prefix = parts[0].lower()
                suffix = parts[1]
                
                # Casos especiales como O', D', L'
                if prefix + "'" in apostrophe_rules:
                    result_words.append(apostrophe_rules[prefix + "'"] + suffix.capitalize())
                    continue
                else:
                    # Capitalizar normalmente ambas partes
                    result_words.append(prefix.capitalize() + "'" + suffix.capitalize())
                    continue
        
        # Manejar prefijos como Mc, Mac
        lower_word = word.lower()
        if lower_word.startswith('mc') and len(word) > 2:
            result_words.append('Mc' + word[2:].capitalize())
            continue
        elif lower_word.startswith('mac') and len(word) > 3:
            result_words.append('Mac' + word[3:].capitalize())
            continue
        
        # Si es la primera palabra, siempre capitalizar
        if i == 0:
            result_words.append(word.capitalize())
        # Si es una preposición/conjunción, mantener en minúsculas
        elif word in lowercase_words:
            result_words.append(word)
        # Para el resto, capitalizar normalmente
        else:
            result_words.append(word.capitalize())
    
    return ' '.join(result_words)

def remove_unnecessary_newlines(text_input):
    """
    Elimina saltos de línea (\n, \r, \r\n) de una cadena de texto,
    reemplazándolos por un solo espacio y limpiando espacios extra.

    Args:
        text_input (str): La cadena de texto a limpiar.

    Returns:
        str or None: La cadena limpia, o None si la entrada es nula o no es una cadena.
    """
    if pd.isna(text_input):
        return None # Maneja NaNs o None de Pandas

    if not isinstance(text_input, str):
        return str(text_input).strip() # Si no es string, intenta convertir y limpiar.

    # 1. Reemplazar todos los tipos de saltos de línea por un espacio
    # r'[\r\n]+' busca uno o más \r o \n
    cleaned_text = re.sub(r'[\r\n]+', ' ', text_input)

    # 2. Eliminar múltiples espacios en blanco y los espacios al principio/final
    # r'\s+' busca uno o más caracteres de espacio en blanco (incluye espacios, tabs, etc.)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text



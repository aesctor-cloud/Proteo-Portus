from number_parser import parse_number
import re
from typing import Any, Optional

def parse_value_input(value_input: Any) -> Optional[float]:
    # Excluir booleanos explícitamente, ya que True/False son instancias de int
    if isinstance(value_input, bool):
        return None
    
    # Si ya es int o float, convierto a float y retorno
    if isinstance(value_input, (int, float)):
        return float(value_input)
    
    if not isinstance(value_input, str):
        return None
    
    if value_input is None or (isinstance(value_input, str) and value_input.strip().lower() in {"", "none", "nan", "null", "n/a"}):
            return None
    
    s = value_input.strip().lower()

    for lang in ['es', 'en']: # Se pueden añadir más lenguajes
        try:
            parsed = parse_number(s, locale=lang)
            if parsed is not None:
                return float(parsed)
        except Exception:
            continue

    try:
        if re.search(r'\d+[a-zA-Z]+|[a-zA-Z]+\d+', s):
            return None  # mezclas inválidas

        # Quitar espacios y caracteres no numéricos salvo sep. decimales
        clean = re.sub(r'[^\d.,\-+eE]', '', s)

        # Manejar formatos conocidos
        if re.fullmatch(r'(\d{1,3},)*\d{3}\.\d+', clean):  # anglosajón
            clean = clean.replace(',', '')
        elif re.fullmatch(r'(\d{1,3}\.)*\d{3},\d+', clean):  # europeo
            clean = clean.replace('.', '').replace(',', '.')
        elif re.fullmatch(r'(\d{1,3},)*\d{3}', clean):  # miles anglosajón sin decimales
            clean = clean.replace(',', '')
        elif re.fullmatch(r'(\d{1,3}\.)*\d{3}', clean):  # miles europeo sin decimales
            clean = clean.replace('.', '')
        elif re.fullmatch(r'\d{1,3}(,\d{3})+$', clean):  # 123,000 o 1,234,567
            clean = clean.replace(',', '')
        elif re.fullmatch(r'\d+[.,]\d+', clean):  # decimal simple
            # Solo usar coma como decimal si no parece miles
            if ',' in clean and '.' not in clean and len(clean.split(',')[-1]) != 3:
                clean = clean.replace(',', '.')
            elif '.' in clean:
                pass  # ya está bien
            else:
                return None
        elif re.fullmatch(r'\d+', clean):  # entero simple
            pass
        else:
            return None  # patrón no reconocido

        return float(clean)
    except Exception:
        return None

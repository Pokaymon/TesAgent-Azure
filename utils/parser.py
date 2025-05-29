import re

def parse_note(texto):
    """
    Extrae monto e identificación de billetera desde la nota.
    Soporta frases como:
    - Ingresar 5000 pesos en la billetera "Ahorros"
    - Ingresar 5.000 a billetera Ahorros
    - Ingresar 10,000.50 pesos a la billetera 'Ahorros'
    """
    # No convertir todo el texto a minúscula
    match = re.search(
        r'ingresar\s+([\d.,]+)\s*(pesos)?\s*.*?\s*(en\s+la|a\s+la|a)?\s*billetera\s*(?:"([^"]+)"|\'([^\']+)\'|([a-záéíóúüñ\s]+))',
        texto,
        re.IGNORECASE
    )

    if match:
        monto_texto = match.group(1).replace('.', '').replace(',', '.')
        try:
            monto = float(monto_texto)
        except ValueError:
            return None, None

        billetera = match.group(4) or match.group(5) or match.group(6)
        billetera = billetera.strip() if billetera else None
        return monto, billetera

    return None, None
import re

def parse_note(texto):
    """
    Extrae monto, tipo de transacción (income/expense) e identificación de billetera desde la nota.
    Soporta frases como:
    - Ingresar 5000 pesos en la billetera "Ahorros"
    - Gastar 2000 en billetera Compras
    """
    match = re.search(
        r'(ingresar|gastar)\s+([\d.,]+)\s*(pesos)?\s*.*?\s*(en\s+la|a\s+la|a)?\s*billetera\s*(?:"([^"]+)"|\'([^\']+)\'|([a-záéíóúüñ\s]+))',
        texto,
        re.IGNORECASE
    )

    if match:
        tipo_str = match.group(1).lower()
        tipo = "income" if "ingresar" in tipo_str else "expense"

        monto_texto = match.group(2).replace('.', '').replace(',', '.')
        try:
            monto = float(monto_texto)
        except ValueError:
            return None, None, None

        billetera = match.group(6) or match.group(7) or match.group(8)
        billetera = billetera.strip() if billetera else None
        return monto, billetera, tipo

    return None, None, None

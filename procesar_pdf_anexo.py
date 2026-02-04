import fitz
import re
import os
import settings


def _extraer_contenido_especifico(full_text, titulo_actual):
    try:
        match_inicio = re.search(
            re.escape(titulo_actual) + r"\s*:?", full_text, re.IGNORECASE
        )
        if not match_inicio:
            return ""
    except re.error:
        return ""

    pos_contenido_inicio = match_inicio.end()
    texto_a_buscar = full_text[pos_contenido_inicio:]

    patron_fin_seccion = r"\n\s*\d+\s+[\d\.]+"
    match_fin = re.search(patron_fin_seccion, texto_a_buscar)

    if match_fin:
        pos_fin_relativa = match_fin.start()
        contenido = texto_a_buscar[:pos_fin_relativa]
    else:
        contenido = texto_a_buscar.split("\n\n")[0]

    contenido_limpio = " ".join(contenido.split()).strip()
    if contenido_limpio and contenido_limpio[0] in [":", "-", "."]:
        contenido_limpio = contenido_limpio[1:].strip()

    return contenido_limpio


def procesar_pdf_anexo(ruta_pdf):
    features_a_extraer = settings.PDF_FEATURES_TO_EXTRACT

    datos_extraidos = {titulo: "-" for titulo in features_a_extraer}

    try:
        with fitz.open(ruta_pdf) as doc:
            full_text = "".join(page.get_text() for page in doc)

        for titulo in features_a_extraer:
            contenido = _extraer_contenido_especifico(full_text, titulo)
            if contenido:
                if titulo == "Plazo para la Ejecución de las Obra":
                    titulo = "Plazo para la Ejecución de las Obras"
                    datos_extraidos[titulo] = contenido
                else:

                    datos_extraidos[titulo] = contenido

    except Exception:
        pass
    finally:
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)

    return datos_extraidos

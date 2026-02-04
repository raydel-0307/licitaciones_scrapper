import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMP_DIR_NAME = "temp"
TEMP_DIR_PATH = os.path.join(BASE_DIR, TEMP_DIR_NAME)

OUTPUT_FILENAME = f"ScrappingMOP_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx"
OUTPUT_FILE_PATH = os.path.join(BASE_DIR, OUTPUT_FILENAME)

RAW_CSV_FILENAME = "ListaLicitaciones_MOP.csv"
RAW_CSV_PATH = os.path.join(TEMP_DIR_PATH, RAW_CSV_FILENAME)

BASE_URL = "https://www.mercadopublico.cl"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/Home/BusquedaLicitacion",
}

SLEEP_TIME_MIN = 1
SLEEP_TIME_MAX = 2


FILTER_KEYWORDS = "Diseño|DISEÑO|Estudio|ESTUDIO|AIF|Análisis|Asesoría"

CSV_COLUMNS_TO_READ = ["IDLicitacion", "NombreLicitacion"]

NEW_COLUMNS = [
    "Region",
    "Fecha de Publicacion",
    "Fecha de Cierre",
    "Especialidad",
    "Sub-Especialidad",
    "Categoría",
    "Dirección de las Obras",
    "Financiamiento",
    "Plazo para la Ejecución de las Obra",
    "Presupuesto Oficial",
    "Visita a Terreno",
]


PDF_SEARCH_KEYWORDS = [
    "anexo_complementario",
    "anexo compl.",
    "modifica anexo complementario",
    "compl",
    "complementario",
    "anx.compl",
]

PDF_FEATURES_TO_EXTRACT = [
    "Presupuesto Oficial",
    "Visita a Terreno",
    "Dirección de las Obras",
    "Financiamiento",
    "Plazo para la Ejecución de las Obras",
    "Plazo para la Ejecución de las Obra",
]

PDF_ALL_POSSIBLE_TITLES = [
    "Presupuesto Oficial",
    "Financiamiento",
    "Visita a Terreno",
    "Plazo para la Ejecución de las Obra",
    "Plazo de Ejecución de las Obras",
    "Plazo",
    "Dirección de las Obras",
    "Tipo de Contrato",
    "Garantías Solicitadas",
    "Presupuesto Disponible",
    "Requisitos para Ofertar",
    "Criterios de Evaluación",
    "Descripción",
    "Adjudicación",
    "Aclaraciones",
]

# Scraper de Licitaciones MOP

![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Libraries](https://img.shields.io/badge/libraries-requests%20%7C%20pandas%20%7C%20beautifulsoup4%20%7C%20PyMuPDF-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

Este proyecto es un scraper web automatizado desarrollado en Python, diseñado para extraer información detallada sobre las licitaciones públicas del **Ministerio de Obras Públicas (MOP)** de Chile desde el portal oficial **MercadoPúblico.cl**.

El script automatiza todo el proceso: desde la descarga de un listado general de licitaciones, el filtrado de las mismas, la visita a la página de detalle de cada una, hasta la descarga y procesamiento de documentos PDF adjuntos (`Anexos Complementarios`) para extraer información clave. El resultado final es un archivo Excel (`.xlsx`) consolidado con todos los datos recopilados.

## ✨ Características Principales

-   **Automatización Completa**: Ejecuta todo el proceso con un solo comando.
-   **Descarga Masiva**: Obtiene un listado actualizado de todas las licitaciones activas del MOP.
-   **Filtrado Inteligente**: Excluye licitaciones no deseadas (como "Diseño" o "Estudio") basándose en palabras clave configurables.
-   **Scraping Detallado**: Navega a la ficha de cada licitación para extraer datos como región, fechas y especialidad.
-   **Manejo de Archivos Adjuntos**: Identifica, descarga y guarda temporalmente los anexos en formato PDF relevantes.
-   **Extracción de Datos de PDF**: Utiliza PyMuPDF (`fitz`) y expresiones regulares para leer el contenido de los PDFs y extraer campos específicos como "Presupuesto Oficial", "Plazo de Ejecución", etc.
-   **Exportación a Excel**: Consolida toda la información extraída, incluyendo las licitaciones filtradas, en un único archivo `.xlsx` limpio y organizado.
-   **Manejo de Sesiones y Headers**: Simula ser un navegador para evitar bloqueos y manejar cookies de sesión.
-   **Modular y Configurable**: El código está organizado en módulos y utiliza un archivo `settings.py` para facilitar la personalización de parámetros.

## 📂 Estructura del Proyecto

./ ├── licitacion_scraper.py # Lógica principal de scraping para cada ficha de licitación. ├── main.py # Punto de entrada principal para orquestar el proceso. ├── mop_downloader.py # Módulo para descargar el CSV inicial con la lista de licitaciones. ├── procesar_pdf_anexo.py # Módulo para extraer datos específicos de los archivos PDF. ├── settings.py # Archivo de configuración central (URLs, keywords, rutas). ├── utils.py # Funciones de utilidad (preparación de datos, exportación a Excel). └── requirements.txt # Dependencias del proyecto.


## 🛠️ Tecnologías Utilizadas

-   **Python 3.9+**
-   **Requests**: Para realizar peticiones HTTP y manejar sesiones.
-   **BeautifulSoup4**: Para el parseo de contenido HTML.
-   **Pandas**: Para la manipulación de datos y la estructuración en DataFrames.
-   **PyMuPDF (fitz)**: Para la lectura y extracción de texto de documentos PDF.
-   **Openpyxl**: Para la escritura de archivos Excel (`.xlsx`).

## 🚀 Instalación

Sigue estos pasos para configurar el entorno de desarrollo y ejecutar el scraper.

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/raydel-0307/licitaciones_scrapper.git
    cd licitaciones_scrapper
    ```

2.  **Crear un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    ```
    -   En Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   En macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Uso

Para iniciar el proceso de scraping, simplemente ejecuta el script `main.py` desde la raíz del proyecto.

```bash
python main.py
```

El script mostrará en la consola el progreso a través de los diferentes pasos:

Descarga del CSV de licitaciones del MOP.
Lectura y filtrado del DataFrame.
Procesamiento individual de cada licitación (esta es la parte más larga).
Exportación de los resultados a Excel.
Al finalizar, encontrarás un archivo llamado ScrappingMOP_Resultado.xlsx en la raíz del proyecto con todos los datos recopilados.

## 📊 Flujo de Trabajo del Scraper
Inicio (main.py): Se crea un directorio temporal ./temp para almacenar archivos intermedios.
Descarga (mop_downloader.py): Se conecta a la API de Mercado Público, obtiene los identificadores de los organismos compradores del MOP y solicita la generación de un archivo CSV con las licitaciones activas, el cual se descarga en el directorio temporal.
Preparación (utils.py): El CSV se carga en un DataFrame de Pandas. Se aplica un filtro para excluir las licitaciones que contengan palabras clave no deseadas (definidas en settings.py). El DataFrame se divide en dos: uno para procesar y otro con las filas excluidas.
Procesamiento (licitacion_scraper.py):
Se itera sobre cada licitación del DataFrame a procesar.
Se accede a la URL de la ficha de la licitación.
Se extraen los datos básicos de la página HTML.
Se realiza una petición POST adicional para obtener datos de "Especialidad".
Se busca el enlace a la sección de archivos adjuntos.
Dentro de los adjuntos, se buscan archivos PDF que coincidan con palabras clave como "anexo complementario".
El PDF encontrado se descarga al directorio temporal.
Extracción de PDF (procesar_pdf_anexo.py):
El PDF descargado se abre y se extrae todo su texto.
Mediante expresiones regulares, se buscan los títulos de las secciones de interés (ej. "Presupuesto Oficial") y se extrae el contenido asociado.
El PDF temporal se elimina después del procesamiento.
Consolidación y Exportación (main.py y utils.py):
Los datos extraídos del HTML y del PDF se combinan.
El resultado se une con las filas que fueron excluidas al principio.
El DataFrame final se exporta a ScrappingMOP_Resultado.xlsx.
Limpieza (main.py): Se elimina el directorio temporal ./temp con todos sus contenidos.
## 🔧 Configuración
Puedes personalizar el comportamiento del scraper modificando las variables en el archivo settings.py:

FILTER_KEYWORDS: Palabras clave para excluir licitaciones (separadas por |).
PDF_SEARCH_KEYWORDS: Palabras clave para identificar el anexo PDF correcto.
PDF_FEATURES_TO_EXTRACT: Lista de campos a extraer del PDF.
SLEEP_TIME_MIN, SLEEP_TIME_MAX: Rango de tiempo de espera (en segundos) entre peticiones para evitar sobrecargar el servidor.
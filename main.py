import os
import shutil
import requests
import settings
from mop_downloader import MOPDownloader
from licitacion_scraper import LicitacionProcessor
import utils
import pandas as pd


def setup_temp_directory():
    if not os.path.exists(settings.TEMP_DIR_PATH):
        print(f"Creando directorio temporal en: {settings.TEMP_DIR_PATH}")
        os.makedirs(settings.TEMP_DIR_PATH)


def cleanup_temp_directory():
    if os.path.exists(settings.TEMP_DIR_PATH):
        shutil.rmtree(settings.TEMP_DIR_PATH)


def run_scraper():
    print("Iniciando el Scraper de Licitaciones MOP")
    setup_temp_directory()

    try:
        downloader = MOPDownloader()
        csv_path = downloader.download_csv()
        if not csv_path:
            print("El proceso no puede continuar sin el archivo CSV.")
            return

        df_inicial, df_excluido = utils.preparar_dataframe(csv_path)
        if df_inicial is None:
            print("El proceso no puede continuar sin un DataFrame válido.")
            return

        with requests.Session() as session:
            session.headers.update(settings.REQUEST_HEADERS)
            processor = LicitacionProcessor(session)
            df_resultado = processor.process_dataframe(df_inicial)

        df_final = pd.concat([df_resultado, df_excluido], ignore_index=True)
        utils.exportar_a_excel(df_final)

    except Exception as e:
        print(f"\n Ocurrió un error inesperado en el proceso principal: {e}")
    finally:
        cleanup_temp_directory()
        print("\nProceso finalizado.")


if __name__ == "__main__":
    run_scraper()

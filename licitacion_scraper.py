import requests
import time
import os
import re
from bs4 import BeautifulSoup
import fitz
from random import randint
from urllib.parse import urljoin
import settings
from procesar_pdf_anexo import procesar_pdf_anexo
import pandas as pd


class LicitacionProcessor:
    def __init__(self, session: requests.Session):
        self.session = session

    def _descargar_y_verificar_anexo(
        self, url_pagina_anexos, button_name, output_filepath
    ):
        try:
            response = self.session.get(url_pagina_anexos, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form", {"name": "form1"})
            if not form:
                return None, None

            post_url = urljoin(url_pagina_anexos, form.get("action"))
            payload = {
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": soup.find("input", {"name": "__VIEWSTATE"}).get("value"),
                "__VIEWSTATEGENERATOR": soup.find(
                    "input", {"name": "__VIEWSTATEGENERATOR"}
                ).get("value"),
                f"{button_name}.x": "10",
                f"{button_name}.y": "10",
            }
            download_response = self.session.post(post_url, data=payload, timeout=45)
            download_response.raise_for_status()
            content_type = download_response.headers.get("Content-Type", "")
            if "text/html" in content_type:
                return None, content_type

            with open(output_filepath, "wb") as f:
                f.write(download_response.content)
            return output_filepath, content_type
        except (requests.exceptions.RequestException, AttributeError, Exception) as e:
            return None, None

    def _obtener_y_procesar_anexo(self, url_adjuntos):
        datos_pdf = {}
        ruta_guardado = None
        try:
            url_adjuntos_completa = (
                "https://www.mercadopublico.cl/Procurement/Modules/"
                + url_adjuntos.split("open('../")[1].split("','", 1)[0]
            )

            response_adjuntos = self.session.get(url_adjuntos_completa)
            response_adjuntos.raise_for_status()
            soup_adjuntos = BeautifulSoup(response_adjuntos.text, "html.parser")
            tabla_adjuntos = soup_adjuntos.find("table", id="DWNL_grdId")
            if not tabla_adjuntos:
                return datos_pdf

            for fila in tabla_adjuntos.find_all("tr")[1:]:
                celdas = fila.find_all("td")
                if len(celdas) < 7:
                    continue

                descripcion = " ".join(
                    [celda.get_text(strip=True) for celda in celdas]
                ).lower()
                input_descarga = celdas[6].find("input")

                if (
                    any(
                        keyword in descripcion
                        for keyword in settings.PDF_SEARCH_KEYWORDS
                    )
                    and input_descarga
                ):
                    nombre_temporal = f"anexo_{randint(10000, 999999)}.pdf"
                    ruta_temporal = os.path.join(
                        settings.TEMP_DIR_PATH, nombre_temporal
                    )

                    ruta_guardado, c_type = self._descargar_y_verificar_anexo(
                        url_adjuntos_completa, input_descarga["name"], ruta_temporal
                    )
                    if ruta_guardado and c_type in [
                        "application/pdf",
                        "application/octet-stream",
                    ]:
                        return ruta_guardado

            return None
        except Exception as e:
            return None

    def _encontrar_valor(self, soup, label_text):
        etiqueta = soup.find(
            "strong", string=lambda text: label_text in text if text else ""
        )
        if etiqueta and etiqueta.parent and etiqueta.parent.find_next_sibling("div"):
            return etiqueta.parent.find_next_sibling("div").text.strip()
        return ""

    def extract_data(self, soup, id_, tag="span"):
        return soup.find(tag, id=id_).text.strip() if soup.find(tag, id=id_) else "-"

    def process_dataframe(self, df):
        print("\n--- PASO 3: Procesando cada Licitación ---")
        results_excel = []
        for idx, row in df.iterrows():
            id_lic = row["IDLicitacion"]

            print(
                f"\nAnalizando Licitación: {id_lic} ({df.index.get_loc(idx) + 1}/{len(df)})"
            )
            try:
                url_ficha = f"{settings.BASE_URL}/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={id_lic}"
                response = self.session.get(url_ficha)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                datos_ficha_actual = {}
                datos_ficha_actual["IDLicitacion"] = (
                    soup.find("span", id="lblNumLicitacion").text.strip()
                    if soup.find("span", id="lblNumLicitacion")
                    else "-"
                )
                datos_ficha_actual["NombreLicitacion"] = self.extract_data(
                    soup, "lblNombreLicitacion"
                )
                datos_ficha_actual["Region"] = self.extract_data(
                    soup, "lblFicha2Region"
                )
                datos_ficha_actual["Fecha de Publicacion"] = self.extract_data(
                    soup, "lblFicha3Publicacion"
                )
                datos_ficha_actual["Fecha de Cierre"] = self.extract_data(
                    soup, "lblFicha3Cierre"
                )

                ultimate_cookies = self.session.cookies.get_dict()["ASP.NET_SessionId"]

                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Referer": response.url,
                    "X-Requested-With": "XMLHttpRequest",
                }

                resp = requests.post(
                    "https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx/ObtenerEspecialidades",
                    headers=headers,
                    cookies={"ASP.NET_SessionId": str(ultimate_cookies)},
                )

                try:
                    especialidad_data = resp.json()["d"][0]["Descripcion"].split("|")

                    datos_ficha_actual["Especialidad"] = especialidad_data[0].strip()
                    datos_ficha_actual["Sub-Especialidad"] = especialidad_data[
                        1
                    ].strip()
                    datos_ficha_actual["Categoría"] = especialidad_data[2].strip()

                except:
                    datos_ficha_actual["Especialidad"] = "-"
                    datos_ficha_actual["Sub-Especialidad"] = "-"
                    datos_ficha_actual["Categoría"] = "-"

                datos_ficha_actual["Dirección de las Obras"] = ""
                datos_ficha_actual["Financiamiento"] = ""
                datos_ficha_actual["Plazo para la Ejecución de las Obra"] = ""
                datos_ficha_actual["Presupuesto Oficial"] = ""
                datos_ficha_actual["Visita a Terreno"] = ""

                input_adjuntos = soup.find("input", id="imgAdjuntos")
                if input_adjuntos and "onclick" in input_adjuntos.attrs:
                    ruta_pdf = self._obtener_y_procesar_anexo(input_adjuntos["onclick"])
                    if ruta_pdf:
                        datos_pdf = procesar_pdf_anexo(ruta_pdf)
                        if datos_pdf:
                            datos_ficha_actual |= datos_pdf

                results_excel.append(datos_ficha_actual)
                time.sleep(randint(settings.SLEEP_TIME_MIN, settings.SLEEP_TIME_MAX))
            except Exception as e:
                print(f"  Error procesando licitación {id_lic}: {e}")
        return pd.DataFrame(results_excel)

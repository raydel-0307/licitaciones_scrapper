import requests
import time
import settings


class MOPDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(settings.REQUEST_HEADERS)
        self.base_url = f"{settings.BASE_URL}/BuscarLicitacion/Home"
        print("MOPDownloader inicializado.")

    def _get_mop_ids(self) -> list[str]:
        try:
            url_comprador = f"{self.base_url}/BuscarComprador"
            response = self.session.get(url_comprador, params={"q": "MOP"})
            response.raise_for_status()
            mop_ids = [i["id"] for i in response.json()]
            print(f"-> Se encontraron {len(mop_ids)} IDs de compradores MOP.")
            return mop_ids
        except requests.exceptions.RequestException as e:
            print(f"Error fatal al buscar compradores: {e}")
            return []

    def _generate_download_file(self, mop_ids: list[str]) -> tuple[str, str] | None:
        payload = {
            "textoBusqueda": "",
            "idEstado": "5",
            "codigoRegion": "-1",
            "idTipoLicitacion": "-1",
            "fechaInicio": None,
            "fechaFin": None,
            "registrosPorPagina": "5000",
            "idTipoFecha": [],
            "idOrden": "1",
            "compradores": mop_ids,
            "garantias": None,
            "rubros": [],
            "proveedores": [],
            "montoEstimadoTipo": [0],
            "esPublicoMontoEstimado": None,
            "pagina": 0,
        }
        try:
            url_generar = f"{self.base_url}/GenerarArchivo"
            response = self.session.post(url_generar, json=payload)
            response.raise_for_status()
            data = response.json()
            file_guid = data.get("FileGuid") or data.get("fileGuid")
            file_name = data.get("nombreArchivo", "ListaLicitaciones.csv")
            if not file_guid:
                print("Error: No se pudo obtener el 'fileGuid' desde la respuesta.")
                return None
            return file_guid, file_name
        except requests.exceptions.RequestException as e:
            print(f"Error fatal al generar el archivo: {e}")
            return None

    def download_csv(self) -> str | None:
        print("\n--- PASO 1: Descargando CSV de Licitaciones MOP ---")
        mop_ids = self._get_mop_ids()
        if not mop_ids:
            return None

        generation_result = self._generate_download_file(mop_ids)
        if not generation_result:
            return None

        file_guid, remote_filename = generation_result
        time.sleep(2)

        url_descargar = f"{self.base_url}/Descargar?fileGuid={file_guid}&nombreArchivo={remote_filename}"
        output_path = settings.RAW_CSV_PATH

        try:
            response = self.session.get(url_descargar)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        except requests.exceptions.RequestException as e:
            print(f"Error fatal al descargar el archivo: {e}")
            return None

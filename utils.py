import pandas as pd
import settings


def exportar_a_excel(df: pd.DataFrame):
    print(f"\n--- PASO 4: Exportando resultados a Excel ---")
    try:
        ruta_output = settings.OUTPUT_FILE_PATH

        df["Fecha de Publicacion"] = pd.to_datetime(
            df["Fecha de Publicacion"],
            errors="coerce",
        ).dt.date
        df["Fecha de Cierre"] = pd.to_datetime(
            df["Fecha de Cierre"], format="mixed", dayfirst=True, errors="coerce"
        ).dt.date

        df.to_excel(ruta_output, index=False)
    except Exception as e:
        print(f"❌ Error al guardar el archivo Excel: {e}")


def preparar_dataframe(
    csv_path: str,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    print("\n--- PASO 2: Leyendo y preparando el DataFrame ---")
    try:
        df = pd.read_csv(
            csv_path, sep=";", on_bad_lines="skip", usecols=settings.CSV_COLUMNS_TO_READ
        )

        filas_antes_del_filtro = len(df)
        print(f"-> Se leyeron {filas_antes_del_filtro} licitaciones del archivo CSV.")

        mascara_filtro = df["NombreLicitacion"].str.contains(
            settings.FILTER_KEYWORDS, case=False, na=False
        )

        df_filtrado = df[~mascara_filtro].copy()
        df_excluido = df[mascara_filtro][settings.CSV_COLUMNS_TO_READ].copy()

        filas_despues_del_filtro = len(df_filtrado)
        filas_eliminadas = filas_antes_del_filtro - filas_despues_del_filtro

        print(
            f"-> Se eliminaron {filas_eliminadas} licitaciones que contienen palabras clave de exclusión (ej: 'Diseño', 'Estudio')."
        )

        for col in settings.NEW_COLUMNS:
            df_filtrado[col] = ""

        return df_filtrado, df_excluido

    except FileNotFoundError:
        return None
    except ValueError as e:
        return None
    except Exception as e:
        return None

# downloader.py
import requests, time
import pandas as pd
from config import BASE_URL, CHUNK_SIZE, SLEEP_TIME, COLUMNS

def download_year(year, where_condition):

    print(f"Descargando {year}")
    offset = 0
    all_chunks = []

    while True:
        params = {
            "$limit": CHUNK_SIZE,
            "$offset": offset,
            "$select": ", ".join(COLUMNS),
            "$where": f"{where_condition} AND date_extract_y(fecha_de_firma) = {year}"
        }

        r = requests.get(BASE_URL, params=params, timeout=120)
        r.raise_for_status()
        data = r.json()

        if not data:
            break

        df = pd.DataFrame(data)
        df['anio'] = year

        df['fecha_de_firma'] = pd.to_datetime(df['fecha_de_firma'], errors='coerce')
        df['valor_del_contrato'] = pd.to_numeric(df['valor_del_contrato'], errors='coerce')

        all_chunks.append(df)
        offset += CHUNK_SIZE
        time.sleep(SLEEP_TIME)

    return pd.concat(all_chunks, ignore_index=True) if all_chunks else pd.DataFrame()
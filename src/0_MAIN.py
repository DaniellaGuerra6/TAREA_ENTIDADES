# main.py
import os
import pandas as pd
from downloader import download_year
from cleaner import estandarizar_texto
from config import (RAW_PATH, EXCLUIR, RENAME_COLUMNS,
                    CATEGORIAS)


print("Iniciando pipeline de procesamiento de datos...")

YEARS = range(2019, 2026)

# -------------------------
# ESCENARIO 1: NACIONAL
# -------------------------
WHERE_NACIONAL = """
        orden = 'Nacional'
        AND tipo_de_contrato = 'Obra'
        AND tipodocproveedor = 'NIT'
        AND estado_contrato IN ('Terminado','Modificado','En ejecución','Cerrado',
                                'terminado','modificado','en ejecución','cerrado')
"""

# -------------------------
# ESCENARIO 2: ATLÁNTICO
# -------------------------
WHERE_ATL = """
    departamento = 'Atlántico'
    AND tipodocproveedor = 'NIT'
    AND estado_contrato IN ('Terminado','Modificado','En ejecución','Cerrado',
                            'terminado','modificado','en ejecución','cerrado')
"""


# FUNCIONES

def filtrar_unspsc(df, categorias):
    df_filtrado = df[
        (
            df['codigo_categoria']
            .astype(str)
            .str.split(".")
            .str[1]
            .str[:6]
            .isin(categorias)
        )
        |
        (df['codigo_categoria'].astype(str).str.lower() == "unspecified")
    ].copy()
    return df_filtrado



def ejecutar_pipeline(nombre_salida, where_condition):
    print(f"Ejecutando pipeline para {nombre_salida}...\n")
    all_years = []

    for year in YEARS:
        df_year = download_year(year, where_condition)
        if not df_year.empty:
            all_years.append(df_year)

    df_final = pd.concat(all_years, ignore_index=True)

    df_final['texto'] = df_final['objeto_del_contrato']

    df_final = df_final[~df_final['sector'].isin(EXCLUIR)].copy()

    df_final.rename(columns=RENAME_COLUMNS, inplace=True)

    for col in ['texto', 'nombre_entidad', 'proveedor_adjudicado']:
        df_final[col] = df_final[col].apply(estandarizar_texto)

        df_final = filtrar_unspsc(df_final, CATEGORIAS)


    output_path = os.path.join(RAW_PATH, f"{nombre_salida}.xlsx")
    df_final.to_excel(output_path, index=False)

    print(f"\nArchivo creado en {output_path}"
          f"\nTotal registros: {df_final.shape[0]}\n"
          f"{'-'*50}\n")


def main():
    # Fase 1: Ejecutar los dos escenarios
    ejecutar_pipeline("SECOP_nacional", WHERE_NACIONAL)
    ejecutar_pipeline("SECOP_territorio", WHERE_ATL)


if __name__ == "__main__":
    main()
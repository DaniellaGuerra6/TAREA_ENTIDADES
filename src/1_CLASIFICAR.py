#========================================================
# IMPORTS
# ==========================================================

import pandas as pd
import os
import re
from config import RAW_PATH, INIT_WORDS, OBJETO, SUB_CAT, MACRO_CAT, DATA_PATH


# ==========================================================
# FUNCIONES BASE
# ==========================================================

def limpiar_inicio(sentence: str, palabras_ini: list) -> str:
    if not isinstance(sentence, str):
        return sentence

    sentence = sentence.strip()

    while True:
        partes = sentence.split(maxsplit=1)
        if partes and partes[0].lower() in palabras_ini:
            sentence = partes[1] if len(partes) > 1 else ""
        else:
            break
    return sentence


def clasificar(texto: str, diccionario: dict) -> dict:

    if not isinstance(texto, str):
        return {"todas": "Otros", "principal": "Otros"}

    texto = texto.lower()
    encontradas = []
    posiciones = {}

    for categoria, palabras in diccionario.items():
        for palabra in palabras:
            match = re.search(rf"\b{re.escape(palabra)}\b", texto)
            if match:
                encontradas.append(categoria)
                pos = match.start()
                if categoria not in posiciones or pos < posiciones[categoria]:
                    posiciones[categoria] = pos
                break

    if not encontradas:
        return {"todas": "Otros", "principal": "Otros"}

    principal = min(posiciones, key=posiciones.get)

    return {
        "todas": "; ".join(encontradas),
        "principal": principal
    }



# ==========================================================
# FUNCIÓN PRINCIPAL ETL
# ==========================================================

def ejecutar_clasificacion(
        ruta_archivo: str,
        output_path: str,
        name
):

    print("\n Cargando base...")
    df = pd.read_excel(ruta_archivo)
    print(f"Dimensión inicial: {df.shape}")

    # LIMPIEZA
    df["texto"] = df["texto"].apply(
        lambda x: limpiar_inicio(x, INIT_WORDS)
    )
    # OBJETO CONTRACTUAL
    df[["objetos", "objeto_contractual"]] = df["texto"].apply(
        lambda x: pd.Series(clasificar(x, OBJETO))
    )
    # SUBCATEGORÍAS
    df[["subcategorias", "SUB"]] = df["texto"].apply(
        lambda x: pd.Series(clasificar(x, SUB_CAT))
    )
    # MACRO
    df["MACRO"] = df["SUB"].map(
        {sub: macro for macro, subs in MACRO_CAT.items() for sub in subs}
    )
    df["MACRO"] = df["MACRO"].fillna("Otros")

    # Eliminar otros
    df = df[~df["MACRO"].isin(["Otros"])].copy()

    print(f"Dimensión final procesada: {df.shape}")

    nombre_archivo = f"SECOP_CAT_{name}"
    
    ruta_salida = os.path.join(output_path, f"{nombre_archivo}.xlsx")
    df.to_excel(ruta_salida, index=False)
    print(f"\n✅ Archivo exportado en:\n{ruta_salida}")



ejecutar_clasificacion(
    ruta_archivo=os.path.join(RAW_PATH, "SECOP_nacional.xlsx"),
    output_path=os.path.join(DATA_PATH),
    name="nacional"
)

ejecutar_clasificacion(
    ruta_archivo=os.path.join(RAW_PATH, "SECOP_territorio.xlsx"),
    output_path=os.path.join(DATA_PATH),
    name="territorio"
)
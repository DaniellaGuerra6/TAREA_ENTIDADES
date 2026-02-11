"""
ETL – Limpieza, estandarización y clasificación de contratos SECOP II

Este script corresponde a la FASE 2 del proyecto ENTIDADES.
Toma como insumo el archivo RAW descargado desde la API de SECOP II y aplica
procesos de depuración orientados al análisis:

- Selección de variables relevantes
- Normalización de texto descriptivo
- Filtro por estado válido del contrato
- Clasificación técnica por familia UNSPSC
"""

# IMPORTS
# -------------------------
import pandas as pd
import re, os
import unicodedata

# RUTAS
# -------------------------
BASE_PATH = r"C:\Users\usuario\OneDrive - POTENCIA\PROYECTOS\TAREA_ENTIDADES"
DATAPATH = os.path.join(BASE_PATH, "data", "RAW")
os.makedirs(DATAPATH, exist_ok=True)
df = pd.read_excel(os.path.join(DATAPATH, "SECOP_RAW__2019_2026.xlsx"))
df = df.drop(columns=['orden', 'tipo_de_contrato'])
print(f"📍 DATASET ORIGINAL - Dimensión: {df.shape}")


# RENOMBRAR / NORMALIZAR
# -------------------------
RENAME_COLUMNS = {
    'modalidad_de_contratacion' : 'modalidad_contrato', 
    'codigo_de_categoria_principal': 'codigo_categoria', 
    'descripcion_del_proceso': 'descripcion', 
    'c_digo_bpin': 'codigo_BPIN',
    'presupuesto_general_de_la_nacion_pgn': 'recursos_PGN', 
    'sistema_general_de_participaciones' : 'recursos_SGP', 
    'sistema_general_de_regal_as': 'recursos_SGR',
    'recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_': 'recursos_territorio',
    'recursos_de_credito': 'recursos_credito', 
}
df = df.apply(lambda col: col.str.lower() if col.dtype == "object" else col)
df = df.rename(columns=RENAME_COLUMNS)

df['nombre_entidad'] = (
    df['nombre_entidad']
    .str.replace(r'[°*+]', ' ', regex=True)
    .str.replace(r'\d+', '', regex=True)
    .str.strip()
    .str.upper()
)



# FILTRO - Estado del contrato
# -------------------------
ESTADOS_CORE = [
    "terminado",
    "modificado",
    "en ejecución",
    "cerrado"
]
df["estado_contrato"] = (df["estado_contrato"].str.strip().str.lower())
filtro = df[df["estado_contrato"].isin(ESTADOS_CORE)].copy()

print("\nTabla 1: Estado de los contratos")
tabla_1 = (
    filtro["estado_contrato"]
    .value_counts(dropna=False)
    .rename("conteo")
    .reset_index()
)
tabla_1["porcentaje"] = (
    tabla_1["conteo"] / tabla_1["conteo"].sum() * 100
    ).round(2)
tabla_1.columns = ["estado_contrato", "conteo", "porcentaje"]
print(tabla_1)

# FILTRO - Categorias
# -----------------------
CATEGORIAS = [
    "77110000",
    "95111601",
    "95111602",
    "95111603",
    "95111604",
    "95111605",
    "95121507",
    "95121509",
    "95121511",
    "95121600",
    "95121700",
    "95121900",
    "95101500",
    "95101600",
    "95101700",
    "95101800"
]
filtro = filtro[
    filtro['codigo_categoria']
        .astype(str)
        .str.split(".")
        .str[-1]
        .isin(CATEGORIAS)
].copy()


print("\nCantidad de contratos:", filtro.shape[0])
print("Porcentaje retenido del RAW:", round(filtro.shape[0] / df.shape[0] * 100, 2), "%")



# FUNCIÓN - Estandarizar texto descriptivo del proceso de contratación
# -------------------------
def estandarizar_descripcion(texto):
    """
    Limpia y estandariza el texto descriptivo del proceso contractual.
    - Conversión a minúsculas
    - Eliminación de signos, números y caracteres especiales
    - Normalización de tildes
    - Normalización de espacios
    args:
        - texto (str): Texto descriptivo original
    returns:
        - str: Texto limpio y estandarizado
    """
    if pd.isna(texto):
        return texto
    original = texto
    # 1. minusculas
    texto = texto.lower()
    # 2. eliminar signos de puntuacion basicos
    texto = re.sub(r'[.,;:]', '', texto)
    # 3. eliminar comillas y caracteres especiales comunes
    texto = re.sub(r'[\"“”\'’]', '', texto)
    # 4. eliminar símbolos no semánticos específicos
    texto = re.sub(r'[°*+]', ' ', texto)
    # 5. normalizar unicode (quita tildes pero conserva ñ)
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn" or ch == "ñ")
    # 6. eliminar números
    texto = re.sub(r'\d+', '', texto)
    # 7. eliminar caracteres no alfabéticos (excepto espacios y ñ)
    texto = re.sub(r'[^a-zñ\s]', ' ', texto)
    # 8. normalizar espacios
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

filtro['texto'] = filtro['descripcion'].apply(estandarizar_descripcion)
filtro = filtro.drop(columns=['descripcion'])

# Correccion de digitación
reemplazos = {
    "manteniendo": "mantenimiento",
    "manteniiento": "mantenimiento",
    "matenimiento": "mantenimiento",
    "construcion": 'construccion',
    'construicion': 'construccion',
    'construiccion': 'construccion',
}
filtro["texto"] = filtro["texto"].replace(reemplazos, regex=True)


# EXPORTAR - Datos con macro filtro
output_file = os.path.join(DATAPATH, "SECOP_CONTRATOS.xlsx")
filtro.to_excel(output_file, index=False)
# Descriptivo
print(f"\n -----------------------"
      f"\nRegistros filtrados"
      f"\nDimensiones: {filtro.shape}"
      f"\nArchivos generados"
      f"\nUbicación: {output_file}")

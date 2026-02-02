"""
Filtro, estandarización y clasificación de contratos

Este script toma como insumo el archivo RAW descargado desde la API de SECOP II
y aplica una serie de filtros y transformaciones para depurar la base de datos:

- Selección de variables relevantes
- Normalización de texto
- Filtro por estado del contrato
- Clasificación por familia UNSPSC

El resultado corresponde a archivo Excel con los contratos filtrados y estandarizados

Autor: Daniella Guerra - Analísta de datos
Empresa: POTENCIA EXPONENCIAL CONSULTORES
"""


# IMPORTS
import pandas as pd
import re, os
import unicodedata

# RUTAS
BASE_PATH = r"C:\Users\usuario\OneDrive - POTENCIA\ARCHIVOS\TAREA_ENTIDADES"
DATAPATH = os.path.join(BASE_PATH, "data", "0_raw")
os.makedirs(DATAPATH, exist_ok=True)
df = pd.read_excel(os.path.join(DATAPATH, "SECOP_RAW__2019_2025.xlsx"))

# SELECCIÓN - Variables de interés
df = df[[
    # Sobre la entidad
    'nombre_entidad', 'nit_entidad', 'codigo_entidad', 'sector',
    # Sobre el contrato
    'id_contrato', 'estado_contrato','modalidad_de_contratacion', 'anio', 
    'codigo_de_categoria_principal','descripcion_del_proceso', 'fecha_de_firma', 
    # Sobre el proveedor
    'tipodocproveedor', 'documento_proveedor', 'codigo_proveedor', 'proveedor_adjudicado', 
    'origen_de_los_recursos', 'destino_gasto', 'valor_del_contrato', 
    # Sobre el contrato
    'c_digo_bpin', 'urlproceso',
    # Sobre las fuentes de financiacion
    'presupuesto_general_de_la_nacion_pgn', 'sistema_general_de_participaciones', 
    'sistema_general_de_regal_as','recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_',
    'recursos_de_credito', 'recursos_propios'
]]

# RENOMBRAR 

# Definición de nombres esta
names = {
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
df = df.rename(columns=names)
print(f"📍 DataFrame filtrado:\n Dimensiones: {df.shape}")



# FILTRO - Estado del contrato
ESTADOS_CORE = [
    "terminado",
    "modificado",
    "en ejecución",
    "cerrado"
]
df["estado_contrato"] = (df["estado_contrato"].str.strip().str.lower())
filter = df[df["estado_contrato"].isin(ESTADOS_CORE)].copy()

print("\nTabla 1: Estado de los contratos")
tabla_1 = (filter["estado_contrato"].value_counts(dropna=False).rename("conteo").reset_index())
tabla_1["porcentaje"] = (tabla_1["conteo"] / tabla_1["conteo"].sum() * 100).round(2)
tabla_1.columns = ["estado_contrato", "conteo", "porcentaje"]
print(tabla_1)
print("\nCantidad de contraros:", filter.shape[0])
print("Porcentaje retenido del RAW:", round(filter.shape[0] / df.shape[0] * 100, 2), "%")




# CLASIFICACIÓN - Familia UNSPSC
# Categoría de contrato según la familia del código (Descripción de qué se hace, deifine la naturaleza técnica)
MAP_FAMILIA_UNSPSC = {
    "7210": "Mantenimiento y reparaciones",
    "7211": "Edificación residencial",
    "7212": "Edificación no residencial",
    "7214": "Infraestructura pesada",
    "7215": "Infraestructura especializada"
}
filter["codigo_familia_UNSPSC"] = (filter["codigo_categoria"].str.extract(r"v1\.(72\d{2})"))
filter["nombre_familia_UNSPSC"] = (filter["codigo_familia_UNSPSC"].map(MAP_FAMILIA_UNSPSC))

print("\nTabla 2: Familia UNSPSC")
tabla_2 = (filter["nombre_familia_UNSPSC"].value_counts(dropna=False).rename("conteo").reset_index())
tabla_2["porcentaje"] = (tabla_2["conteo"] / tabla_2["conteo"].sum() * 100).round(2)
tabla_2.columns = ["nombre_familia_UNSPSC", "conteo", "porcentaje"]
print(tabla_2)



# FUNCIÓN - Estandarizar texto descriptivo del proceso de contratación
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

filter['texto'] = filter['descripcion'].apply(estandarizar_descripcion)
filter = filter.drop(columns=['descripcion'])

# Correccion de digitación
reemplazos = {
    "manteniendo": "mantenimiento",
    "manteniiento": "mantenimiento",
    "matenimiento": "mantenimiento",
    "construcion": 'construccion',
    'construicion': 'construccion',
    'construiccion': 'construccion',
}
filter["texto"] = filter["texto"].replace(reemplazos, regex=True)



# EXPORTAR - Datos con macro filtro

output_file = os.path.join(DATAPATH, "SECOP_filtro__2019_2025.xlsx")
filter.to_excel(output_file, index=False)
# Descriptivo
print(f"\n -----------------------"
      f"\nRegistros filtrados"
      f"\nDimensiones: {filter.shape}"
      f"\nColumnas: {filter.columns}")

"""

"""

# IMPORTS
# -------------------------
import os, requests, time
import pandas as pd

# RUTAS
# -------------------------
BASE_PATH = r"C:\Users\usuario\OneDrive - POTENCIA\PROYECTOS\TAREA_ENTIDADES"
RAW_PATH = os.path.join(BASE_PATH, "data", "RAW")
os.makedirs(RAW_PATH, exist_ok=True)

# CONFIGURACIÓN DE LA API
# -------------------------
BASE_URL = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
CHUNK_SIZE = 5000
MAX_RETRIES = 3
SLEEP_TIME = 1

# COLUMNAS DE INTERÉS
COLUMNS = [
    # Sobre la entidad
    'nombre_entidad', 'nit_entidad', 'codigo_entidad', 'orden', 'sector',
    # Sobre el contrato
    'id_contrato', 'estado_contrato','modalidad_de_contratacion', 'tipo_de_contrato',
    'codigo_de_categoria_principal','descripcion_del_proceso', 'fecha_de_firma', 
    # Sobre el proveedor
    'tipodocproveedor', 'documento_proveedor', 'codigo_proveedor', 'proveedor_adjudicado', 
    'origen_de_los_recursos', 'destino_gasto', 'valor_del_contrato', 
    # Sobre el proyecto
    'c_digo_bpin', 'urlproceso',
    # Sobre las fuentes de financiacion
    'presupuesto_general_de_la_nacion_pgn', 'sistema_general_de_participaciones', 
    'sistema_general_de_regal_as','recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_',
    'recursos_de_credito', 'recursos_propios'
    ]


# FUNCION - Descargar datos
def download_year(year):
    """
    Descarga los registros de contratos SECOP II correspondientes a un año específico.
    Filtra los registros según criterios predefinidos,
    args: 
        - year (int): Año de la firma del contraro a descargar
    returns:
        - pd.DataFrame: registros del año solicitado.
    """

    print(f'Descargando {year}')
    offset = 0
    all_chunks = []

    while True:
        # Parámetros condicionales para la selección de datos
        params = {
            "$limit": CHUNK_SIZE,
            "$offset": offset,
            "$select": ", ".join(COLUMNS),
            "$where":  
                        #f"orden='Territorial' "
                        f"orden='Nacional' "
                        f"AND tipo_de_contrato='Obra' "
                        f"AND date_extract_y(fecha_de_firma)={year}"  
        }

        r = requests.get(BASE_URL, params=params, timeout=120)
        r.raise_for_status()
        data = r.json()
        
        if not data:
            break  # condición real de salida

        df = pd.DataFrame(data)
        df['anio'] = year

        # Conversión de columnas
        df['fecha_de_firma'] = pd.to_datetime(df['fecha_de_firma'], errors='coerce')
        df['valor_del_contrato'] = pd.to_numeric(df['valor_del_contrato'], errors='coerce')

        all_chunks.append(df)
        offset += CHUNK_SIZE

        time.sleep(SLEEP_TIME)

    return pd.concat(all_chunks, ignore_index=True) if all_chunks else pd.DataFrame()


# [MAIN]
all_years = []

for year in range(2019, 2026):  # Años de interés
    df_year = download_year(year)
    if not df_year.empty:
        all_years.append(df_year)

df_final = pd.concat(all_years, ignore_index=True)


# Descriptivo del dataset
print(f"\n -----------------------"
      f"\nRegistros descargados"
      f"\nDimensiones: {df_final.shape}"
      f"\nColumnas: {list(df_final.columns)}")

# EXPORTAR - Datos RAW consolidados
output_file = os.path.join(RAW_PATH, "SECOP_RAW_ALL__2019_2026.xlsx")
#output_file = os.path.join(RAW_PATH, "SECOP_RAW_ALL__TERRITORIAL.xlsx")
df_final.to_excel(output_file, index=False)
print(f"📁 Archivo creado en:\n{output_file}")


excluir = ['defensa', 'Información Estadística', 'Relaciones Exteriores', 
            'Tecnologías de la Información y las Comunicaciones', 
             'Minas y Energía',
            'Ley de Justicia', 'Hacienda y Crédito Público', 
            'Inteligencia Estratégica y Contrainteligencia',
]
df_TOTAL = df_final[~df_final["sector"].isin(excluir)].copy()

# Descriptivo del dataset
print(f"\n -----------------------"
      f"\nRegistros descargados"
      f"\nDimensiones: {df_TOTAL.shape}"
      f"\nColumnas: {list(df_TOTAL.columns)}")

# EXPORTAR - Datos RAW consolidados
output_file = os.path.join(RAW_PATH, "SECOP_RAW__2019_2026.xlsx")
#output_file = os.path.join(RAW_PATH, "SECOP_RAW__TERRITORIAL.xlsx")
df_TOTAL.to_excel(output_file, index=False)
print(f"📁 Archivo creado en:\n{output_file}")
    

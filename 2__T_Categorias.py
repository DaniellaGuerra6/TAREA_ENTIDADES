"""
ETL – Limpieza avanzada de texto y categorización semántica de contratos SECOP II

Este script corresponde a la FASE 3 del proyecto ENTIDADES.
Parte de la base de contratos filtrados y estandarizados (FASE 2) y aplica
reglas semánticas para:

- Limpiar expresiones genéricas no informativas al inicio del texto
- Clasificar el objeto contractual principal
- Identificar subcategorías temáticas del proyecto
- Agrupar los contratos en macro categorías sectoriales
"""

# IMPORTS
# -------------------------
import pandas as pd
import os, re

# RUTAS 
# -------------------------
BASE_PATH = r"C:\Users\usuario\OneDrive - POTENCIA\PROYECTOS\TAREA_ENTIDADES"
DATAPATH = os.path.join(BASE_PATH, "data", "RAW")
OUT_PATH = os.path.join(BASE_PATH, "data", "ARCHIVOS")
os.makedirs(DATAPATH, exist_ok=True)
os.makedirs(OUT_PATH, exist_ok=True)
df = pd.read_excel(os.path.join(DATAPATH, "SECOP_CONTRATOS.xlsx"))
print(f"📍 DataFrame Inicial:\n Dimensiones: {df.shape}")


# FUNCIONES 
# -------------------------

def limpiar_inicio(sentence, palabras_ini):
    """
    Elimina palabras iniciales no informativas de una oración.

    Se remueven de forma iterativa todas las palabras al inicio de la oración
    que coincidan con alguna de las palabras en la lista proporcionada.
    
    Args:
        - sentence (str): La oración a limpiar.
        - palabras_ini (list): Lista de palabras a eliminar del inicio.
    Returns:
        - str: La oración limpia sin las palabras iniciales no informativas.
    """
    if not isinstance(sentence, str):
        return sentence
    sentence = sentence.strip()

    # eliminar todas las palabras iniciales consecutivas que estén en la lista
    while True:
        partes = sentence.split(maxsplit=1)
        if partes and partes[0].lower() in palabras_ini:
            sentence = partes[1] if len(partes) > 1 else ""
        else:
            break
    return sentence

def clasificar(texto, sector):
    """
    Clasifica un texto segun la primera coincidencia semántica encontrada.
    Busca coincidencias exactas de palabras o frases en el texto, y registra:
    - Todas las categorías encontradas
    - La categoría principal basada en la primera aparición en el texto

    Args:
        - texto (str): El texto a clasificar.
        - sector (dict): Diccionario con categorías como claves y listas de palabras clave como valores.
    Returns:
        - dict: Diccionario con:
            - 'todas': Cadena con todas las categorías encontradas separadas por '; '
            - 'principal': La categoría de la primera coincidencia encontrada
    """
    if not isinstance(texto, str):
        return {"todas": "Otros", "principal": "Otros"}

    texto = texto.lower()
    encontradas = []
    posiciones = {}

    for cat, palabras in sector.items():
        for palabra in palabras:
            # Coincidencia exacta de palabra o frase
            match = re.search(rf"\b{re.escape(palabra)}\b", texto)
            if match:
                encontradas.append(cat)
                pos = match.start()
                if cat not in posiciones or pos < posiciones[cat]:
                    posiciones[cat] = pos
                break

    if not encontradas:
        return {"todas": "Otros", "principal": "Otros"}

    todas = "; ".join(encontradas)
    principal = min(posiciones, key=posiciones.get)

    return {"todas": todas, "principal": principal}



# LIMPIEZA DEL TEXTO
# -------------------------

# 1. Palabras inciales no informativas
INIT_WORDS = [
    'el', 'la', 'las', 'los', 'a', 'de', 'del', 'para', 'bs', 'c', 'e', 'es', 'sg', 
    'srt', 'mr', 'd', 'dt', 'nsa', 's', 'sa', 'se', 'lote', 'rmtc', 'rstc', 'rtvc', 
    'rvlc', 'no', 'spa', 'oap', 'sol', 'nr', 'ce', 'srn', 'srnc', 'ranc', 'ratc', 
    'rcnc', 'fun', 'fortis', 'amf', 'amfis', 'sm', 'dtnsa', 'realizar', 'rrealizar', 
    'realizacion', 'ealizar', 'actividades', 'grupo', 'servicio', 'servicios',
    'ejecucion', 'ejecutar', 'esfuerzos', 'prestar', 'global', 'segunda', 'fase',
    'obra', 'obras', 'publica', 'civil', 'civiles', 'complementarias',
    'llevar a cabo', 'mano', 'necesarias', 'segunda', 'mediante', 'por', 'sistema', 
    'sin', 'formula', 'ajuste', 'reajuste', 'todo', 'costo',
    'aunar', 'anuar', 'unar', 'esfuerzo', 'y' , 'apoyo mutuo', 
    'precios', 'precio', 'unitario', 'unitarios', 'fijo', 'fijos', 'contratar', 'bajo', 
]
df['texto'] = df['texto'].apply(
    lambda x: limpiar_inicio(x, INIT_WORDS)
    )

# Verificación de limpieza
print("\nTabla de conteo post-limpieza de texto:")
conteo_1 = df['texto'].value_counts()
print(f"Coincidencias {conteo_1.shape}")



# 2. Categorización por objeto contractual
OBJETO = {
    'Adecuacion': {'adecuacion', 'adecuar', 'adecuaciones', 'acondicionamiento', 'habilitar'},
    'Construccion': {'construccion', 'construir', 'construcciones', 'reconstruir', 'reconstruccion',
                     'demoler', 'demolicion', 'desmontaje', 'desmonte', 'desmontar', 'instalacion'},
    'Mantenimiento': {'mantenimiento', 'mantener'},
    'Reparacion': {'reparacion', 'reparaciones', 'reparar', 'rehabilitar', 'recuperacion', 'rehabilitacion', 'restauracion'},
    'Atencion': {'atencion', 'atender'},
    'Mejoramiento': {'mejoramiento', 'mejorar', 'remodelar', 'remodelacion', 'ampliar', 'ampliacion', 'modernizacion'},
}

df[["objetos", "objeto_contractual"]] = df["texto"].apply(
    lambda x: pd.Series(clasificar(x, OBJETO))
)

print("Tabla de conteo por objeto contractual:")
tabla = (df["objeto_contractual"]
         .value_counts(dropna=False)
         .rename("conteo").reset_index()
         )
tabla["porcentaje"] = (
    tabla["conteo"] / tabla["conteo"].sum() * 100
    ).round(2)
tabla.columns = ["objeto_contractual", "valor_neto", "porcentaje"]
print(tabla)



# 3. Categorización por SUB-Categorias
dic_subcategorias = {
    'Publico': {
            'batallon', 'batallones', 'infanteria', 'estacion de policia', 'policia',
            'aerocivil', 'insituto nacional de medicina legal', 'oficinas', 
            'base naval', 'palacio de justucia', 'juzgado', 'superintendencia', 
            'militar', 'militares', 'consejo', 'inpec', 'pabellon', 'pabellones'
            'hospital', 'centro de salud', 'eps', 'clinica', 'salud',
            'naval', 'navales', 'guardacostas', 'policial', 'artillería', 
            'ejercito', 'militar', 'escuela naval', 'policiales', 'escuela de policia',
            'escuela militar'
            },

    'Rio': {
            'rio', 'cuenca', 'cuenca hidrografica', 'canal', 'canal hidraulico', 'afluente', 
            'corriente hidrica', 
            'control de inundaciones', 'proteccion de rivera', 'obras hidraulicas'
            },

    'Reservas y ecoparques': {
            'reserva natural', 'area protegida', 'ecoparque', 'restauracion ambiental', 
            'reforestacion','biodiversidad', 'conservacion ambiental','ecosistema', 
            'gestion ambiental','zona costera', 'manejo ambiental', 'ecologico', 
            'sendero', 'ecoturistico', 'natural'
            },

    'Energia renovable': {
            'energia renovable', 'energia solar', 'panel solar', 'sistema fotovoltaico',
            'energia eolica', 'generacion electrica limpia'
        },

    'Servicios publicos': {
            'servicio publico', 'servicios publicos', 'domiciliario', 'acueducto', 'alcantarillado', 
            'tratamiento de aguas', 'agua potable', 'residuos solidos', 'aseo urbano', 
            'disposicion final', 'gas domiciliario'
        },

    'Agro': {
            'agropecuario', 'agricola','ganaderia', 'desarrollo rural',
            'sistema de riego', 'distrito de riego','asistencia tecnica rural'
        },

    'Turismo': {
            'turismo', 'infraestructura turistica','atractivo turistico', 'ecoturismo',
            'turismo cultural', 'ruta turistica'
        }, 
   
    'Aeropuerto': {
            'aeropuerto', 'infraestructura aeroportuaria', 'terminal aereo', 'aviacion civil'
        },

    'Puente': {
            'puente vehicular', 'puente peatonal', 'paso elevado', 'interseccion vial','rotonda vehicular', 'puente'
        },

    'Puerto': {
            'puerto', 'infraestructura portuaria', 'muelle', 'embarcadero', 
            'terminal fluvial', 'navegacion fluvial'
        },

    'Transporte publico': {
            'transporte publico', 'movilidad urbana','sistema de transporte masivo',
            'terminal de transporte', 'bus','metro', 'cicloruta', 'bicicarril'
        },

    'Tren': {
            'tren', 'ferrocarril', 'infraestructura ferroviaria', 'red ferroviaria'
        },

    'Vias': {
            'vias', 'via', 'via nacional', 'carretera', 'red vial', 'corredor vial', 'pavimentacion', 
            'mejoramiento vial', 'glorieta', 'interseccion vial'
        },
    'Vias terciarias': {
            'via terciaria', 'red vial terciaria', 'camino rural', 'mejoramiento de vias rurales'
        },
    
    'Parques y plazas': {
            'parque urbano', 'plaza publica', 'espacio publico', 'zona recreativa',
            'escenario recreativo', 'plazoleta'
        },

    'Vias urbanas': {
            'via urbana', 'infraestructura urbana', 'anden', 'andenes',
            'malla vial urbana', 'pavimentacion urbana'
        },

    'Vivienda': {
            'vivienda', 'proyecto habitacional', 'mejoramiento de vivienda',
            'urbanizacion', 'solucion de vivienda'
        },

    'Educacion': {
            'educacion', 'institucion educativa', 'colegio', 'escuela', 'universidad', 
            'infraestructura educativa', 'aulas', 'sede educativa'
        },

    'Deporte': {
            'deporte', 'escenario deportivo', 'polideportivo', 'coliseo',
            'cancha deportiva', 'unidad deportiva'
    },
}

df[["subcategorias", "SUB"]] = df["texto"].apply(
    lambda x: pd.Series(clasificar(x, dic_subcategorias))
)



# 4. Categorización por MACRO-Categorías
dic_macro = {
    'Ambiental y gestion del territorio': {
        'Rio',
        'Reservas y ecoparques'
    },
    'Productiva y de servicios': {
        'Energia renovable',
        'Servicios publicos',
        'Agro',
        'Turismo'
    },
    'Transporte': {
        'Aeropuerto',
        'Puente',
        'Puerto',
        'Transporte publico',
        'Tren',
        'Vias',
        'Vias terciarias'
    },
    'Urbanismo y desarrollo metropolitano': {
        'Parques y plazas',
        'Vias urbanas',
        'Vivienda',
        'Educacion',
        'Deporte'
    },
    'Otros': {
        'Otros',
        'Publico'
    }
}
df['MACRO'] = df['SUB'].map(
    {sub: macro for macro, subs in dic_macro.items() for sub in subs}
    )


# FILTRO FINAL
# -------------------------

contratos = df[~df['MACRO'].isin(['Otros'])]
print(f"📍 DataFrame filtrado por MACRO categorias:\n Dimensiones: {contratos.shape}")
print(f"Representa: {round((contratos.shape[0] / df.shape[0] * 100),2)}%")

print("Tabla de conteo por MACRO categorias proyecto:")
tabla = (contratos["MACRO"]
         .value_counts(dropna=False)
         .rename("conteo").reset_index()
         )
tabla["porcentaje"] = (
    tabla["conteo"] / tabla["conteo"].sum() * 100
    ).round(2)
tabla.columns = ["MACRO", "conteo", "porcentaje"]
print(tabla)

# Exportar resultados
contratos.to_excel(os.path.join(OUT_PATH, 'SECOP_CATEGORIZED.xlsx'), index=False)

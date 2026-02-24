# DICCIONARIOS
import os

# ---------------------------------
BASE_PATH = r"C:\Users\usuario\OneDrive - POTENCIA\PROYECTOS\TAREA_ENTIDADES"
RAW_PATH = os.path.join(BASE_PATH, "data", "RAW")
DATA_PATH = os.path.join(BASE_PATH, "data", "ARCHIVOS")
os.makedirs(RAW_PATH, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)

BASE_URL = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
CHUNK_SIZE = 5000
SLEEP_TIME = 1

# 0. Sectores a excluir
EXCLUIR = [
    'defensa', 'Información Estadística', 'Relaciones Exteriores', 
    'Tecnologías de la Información y las Comunicaciones', 
    'Minas y Energía',
    'Ley de Justicia', 'Hacienda y Crédito Público', 
    'Inteligencia Estratégica y Contrainteligencia',
]

# 1. Configuración de columnas a descargar
COLUMNS = [
    # Sobre la entidad
    'nombre_entidad', 'orden', 'sector',
    # Sobre el contrato
    'id_contrato', 'estado_contrato', 'tipo_de_contrato',
    'codigo_de_categoria_principal', 'fecha_de_firma', 
    'objeto_del_contrato',
    # Sobre el proveedor
    'tipodocproveedor', 'proveedor_adjudicado', 'valor_del_contrato', 

    # Sobre las fuentes de financiacion
    'presupuesto_general_de_la_nacion_pgn', 'sistema_general_de_participaciones', 
    'sistema_general_de_regal_as','recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_',
    'recursos_de_credito', 'recursos_propios'
    ]

# 2. Renombrar columnas
RENAME_COLUMNS = {
    'codigo_de_categoria_principal': 'codigo_categoria', 
    'presupuesto_general_de_la_nacion_pgn': 'recursos_PGN', 
    'sistema_general_de_participaciones' : 'recursos_SGP', 
    'sistema_general_de_regal_as': 'recursos_SGR',
    'recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_': 'recursos_territorio',
    'recursos_de_credito': 'recursos_credito', 
}

# 3. Catetgorias base y de territorio extra
CATEGORIAS = [
    "701117","721015","721029","721211","721410",
    "721411","721412","721515","771100","831015",
    "951015","951016","951017","951018",
    "951115","951116","951215","951216",
    "951217","951219","951223","unspecified",
    "811015","801016"
]


# 4. Palabras a eliminar al inicio del objeto contractual
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

# 5. Objeto de contrato
OBJETO = {
    'Adecuacion': {'adecuacion', 'adecuar', 'adecuaciones', 'acondicionamiento', 'habilitar'},
    'Construccion': {'construccion', 'construir', 'construcciones', 'reconstruir', 'reconstruccion',
                     'demoler', 'demolicion', 'desmontaje', 'desmonte', 'desmontar', 'instalacion'},
    'Mantenimiento': {'mantenimiento', 'mantener'},
    'Reparacion': {'reparacion', 'reparaciones', 'reparar', 'rehabilitar', 'recuperacion', 'rehabilitacion', 'restauracion'},
    'Atencion': {'atencion', 'atender'},
    'Mejoramiento': {'mejoramiento', 'mejorar', 'remodelar', 'remodelacion', 'ampliar', 'ampliacion', 'modernizacion'},
}

# 6. Subcategorias y macro categorias
SUB_CAT = {
    'Publico': {
            'batallon', 'batallones', 'infanteria', 'estacion de policia', 'policia',
            'aerocivil', 'insituto nacional de medicina legal', 'oficinas', 
            'base naval', 'palacio de justucia', 'juzgado', 'superintendencia', 
            'militar', 'militares', 'consejo', 'inpec', 'pabellon', 'pabellones'
            'hospital', 'centro de salud', 'eps', 'clinica', 'salud',
            'naval', 'navales', 'guardacostas', 'policial', 'artillería', 
            'ejercito', 'militar', 'escuela naval', 'policiales', 'escuela de policia',
            'escuela militar',
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
            'sendero', 'ecoturistico', 'natural', 'senderos ecologicos'
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
            'sistema de riego', 'distrito de riego','asistencia tecnica rural',
            'acuicultura', 'viveros'
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
            'terminal fluvial', 'navegacion fluvial', 'muelles fluviales'
        },

    'Transporte publico': {
            'transporte publico', 'movilidad urbana','sistema de transporte masivo',
            'terminal de transporte', 'bus','metro', 'cicloruta', 'bicicarril'
        },

    'Tren': {
            'tren', 'ferrocarril', 'infraestructura ferroviaria', 'red ferroviaria',
            'ferrea', 'ferreos'
        },

    'Vias': {
            'vias', 'via', 'via nacional', 'carretera', 'red vial', 'corredor vial', 'pavimentacion', 
            'mejoramiento vial', 'glorieta', 'interseccion vial', 
            'corredor', 'variante', 'ruta', 'carreteras', 'troncal', 'tramos viales',

        },
    'Vias terciarias': {
            'via terciaria', 'red vial terciaria', 'camino rural', 'mejoramiento de vias rurales',
            'corredores rurales'
        },
    
    'Parques y plazas': {
            'parque urbano', 'plaza publica', 'espacio publico', 'zona recreativa',
            'escenario recreativo', 'plazoleta', 'parque infantil', 'parque'
        },

    'Vias urbanas': {
            'via urbana', 'infraestructura urbana', 'anden', 'andenes',
            'malla vial urbana', 'pavimentacion urbana', 'carrera', 'calle',
        },

    'Vivienda': {
            'vivienda', 'proyecto habitacional', 'mejoramiento de vivienda',
            'urbanizacion', 'solucion de vivienda'
        },

    'Educacion': {
            'educacion', 'institucion educativa', 'institución educativa agropecuaria',
            'colegio', 'escuela', 'universidad', 
            'infraestructura educativa', 'aulas', 'sede educativa', 'ie', 'iea', 'campus', 
            'casa de cultura', 'biblioteca', 'museo', 'biblioteca', 'ludoteca'
        },

    'Deporte': {
            'deporte', 'escenario deportivo', 'escenarios deportivos', 'polideportivo', 'coliseo',
            'cancha deportiva', 'unidad deportiva', 'cancha'
    },
}

MACRO_CAT = {
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
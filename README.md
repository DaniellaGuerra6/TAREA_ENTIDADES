# Proyecto Entidades – Contratos de Obra Pública (SECOP II)

Este proyecto tiene como **identificar las entidades que en mayor medida contratan cada de obra pública en Colombia**, a partir de los datos abiertos publicados en SECOP II.


## Fuente de información

La información utilizada proviene de **Datos Abiertos Colombia**, específicamente del conjunto de datos de **SECOP II – Contratos** ([text](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/about_data)), accesible mediante la API publicada. Concentra un esquema de datos estandarizado que detalla datos de entidades contratantes, información contractual, valores económicos y el origen de las fuentes de financiación.

Como filtro pricipal se utiliza el **United Nations Standard Products and Services Code (UNSPSC)** un Sistema de clasificación internacional que organiza bienes y servicios en una jerarquía de segmentos, familias, clases y productos. 

---
## Estructura general del proyecto

El proyecto se desarrolla en **tres pasos consecutivos**, donde cada uno toma como insumo el resultado del anterior:

1. **Extracción de datos (RAW)**
2. **Limpieza y filtrado de contratos**
3. **Limpieza semántica y categorización analítica**

### Paso 1 – Extracción de datos desde SECOP II:
```
0__E_RAWDATA.py
```

En esta etapa se descargan los **datos originales de contratos** directamente desde la plataforma de Datos Abiertos Colombia, sin realizar aún procesos de limpieza o clasificación compleja. La extracción se realiza de forma controlada, año por año, para garantizar estabilidad y completitud de la información, por medio de la API REST de Socrata.

#### Criterios de selección: 

Los contratos descargados cumplen con los siguientes criterios:
* Entidades del **orden nacional**
* Tipo de contrato: **Obra**
* Contratos firmados entre **2019 y 2026**
* Clasificación sectorial (UNSPSC: *Servicios de Edificación, Construcción de Instalaciones y Mantenimiento*.

Entre otras variables, se incluyen:

* Datos de la entidad contratante
* Información básica del contrato
* Descripción del proceso contractual
* Valor del contrato
* Fuentes de financiación
* Identificadores del proyecto

El producto de esta etapa es un archivo en Excel con los datos **tal como vienen de la fuente**, consolidado para todos los años analizados. 

📁 **Archivo generado:**
```
SECOP_RAW__2019_2026.xlsx
```

> Nota: En esta fase no se eliminan registros ni se corrigen textos. El objetivo es conservar la información original.

---

### Paso 2 – Limpieza y filtrado de contratos
```
1_E_FiltroContrato.py
```

A partir del archivo descargado desde SECOP II, se aplican reglas para asegurar que los contratos incluidos sean comparables y relevantes desde el punto de vista analítico.

#### Principales procesos realizados

* **Selección de variables clave**: se conservan únicamente los campos necesarios para analizar entidades, contratos, proveedores, valores y fuentes de financiación.

* **Normalización de información**: se estandarizan nombres de columnas y se homogeniza el uso de mayúsculas, tildes y formatos de texto.

* **Filtro por estado del contrato**: solo se incluyen contratos con ejecución real o cierre administrativo (por ejemplo: *en ejecución*, *terminado*, *modificado* o *cerrado*).

* **Exclusión de fuerza pública**: se eliminan contratos asociados a entidades militares y de policía para concentrar el análisis en infraestructura civil.

* **Clasificación técnica (UNSPSC)**: cada contrato se agrupa según la familia de su código UNSPSC, permitiendo distinguir grandes tipos de obra.

* **Limpieza del texto descriptivo**: se depuran errores de digitación y se normalizan las descripciones para facilitar análisis posteriores.


📁 **Archivo generado:**

```
SECOP_CONTRATOS.xlsx
```

---

## Paso 3 – Categorización semántica de los contratos
```
2__T_Categorias.py
```
 El objetivo es traducir descripciones contractuales extensas y heterogéneas en **categorías claras**, comparables y útiles para análisis estratégico.

### Principales procesos realizados

* **Limpieza semántica del texto**: se eliminan expresiones genéricas o poco informativas al inicio de las descripciones (por ejemplo: “realizar”, “ejecutar”, “obra”, “servicios”).

* **Identificación del objeto contractual**: se clasifica el contrato según su acción principal, como construcción, mantenimiento, adecuación, mejoramiento o reparación.

* **Asignación de subcategorías temáticas**: se identifican temas específicos del proyecto, como vías, vivienda, educación, parques, ríos, servicios públicos, turismo, entre otros. (Ver `clasificacion_categorias_proyecto.txt`)

* **Agrupación en macro categorías**: las subcategorías se consolidan en grandes grupos sectoriales que facilitan el análisis agregado, tales como:

  * Transporte
  * Urbanismo y desarrollo metropolitano
  * Ambiental y gestión del territorio
  * Productiva y de servicios

* **Depuración final**: se excluyen contratos que no logran asociarse a una categoría analítica clara.

El resultado es la **base final categorizada del proyecto**, lista para análisis sectorial, cruces territoriales y visualización en herramientas de BI.

📁 **Archivo generado:**

```
SECOP_CATEGORIZED.xlsx
```

Este archivo permite responder preguntas estratégicas sobre **qué se contrata**, **en qué sectores**, y **dónde se concentran los recursos públicos**.



## Autoría

**Daniella Guerra**
Analista de Datos
POTENCIA EXPONENCIAL CONSULTORES

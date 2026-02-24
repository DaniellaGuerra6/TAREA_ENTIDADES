import pandas as pd
import os
from config import DATA_PATH

def contratos(
        df, ruta_salida
):
    
    print(
        "📍 DataFrame inicial:"
        f" - Número de filas: {df.shape[0]}"
        f" - Número de columnas: {df.shape[1]}"
        )
    
    df['proveedor_adjudicado'] = df['proveedor_adjudicado'].str.strip().str.upper()
    df['proveedor_adjudicado'] = df[~df['proveedor_adjudicado'].str.contains('CONSORCIO|UNION TEMPORAL|UT')]['proveedor_adjudicado']
    
    # TABLA 1: Entidades con contrato de mayor valor
    entidades = (
        df.groupby('proveedor_adjudicado', as_index=False)
        .agg(
            valor_total=('valor_del_contrato', 'sum'),  # Agrupación por valor
            contratos=('id_contrato', 'count') 
        )
        .sort_values('valor_total', ascending=False)
        .head(30) 
        .rename(columns={
            'proveedor_adjudicado': 'Proveedor',
            'valor_total': 'Valor Total',
            'contratos': 'Número de Contratos'
        })
    )

    # TABLA 2: Contratos por modalidad
    macro = (
        df.groupby(
            ['proveedor_adjudicado', 'MACRO'],
            as_index=False
        )
        .agg(
            valor_total=('valor_del_contrato', 'sum'),
            contratos=('id_contrato', 'count')
        )
        .sort_values('valor_total', ascending=False)
        .groupby('MACRO', group_keys=False)
        .head(10)
        .rename(columns={
            'MACRO': 'Categoría',
            'proveedor_adjudicado': 'Proveedor',
            'valor_total': 'Valor Total',
            'contratos': 'Número de Contratos'
        })
    )
    
    # TABLA 3: Contratos por modalidad y submodalidad
    entidad_macro_sub = (
        df.groupby(
            ['proveedor_adjudicado', 'MACRO', 'SUB'],
            as_index=False
        )
        .agg(
            valor_total=('valor_del_contrato', 'sum'),
            contratos=('id_contrato', 'count')
        )
        .sort_values('valor_total', ascending=False)
        .groupby(
            ['MACRO', 'SUB'],
            group_keys=False
        )
        .head(5)
        .rename(columns={
            'MACRO': 'Categoría',
            'SUB': 'Subcategoría',
            'proveedor_adjudicado': 'Proveedor',
            'valor_total': 'Valor Total',
            'contratos': 'Número de Contratos'
        })
    )

    with pd.ExcelWriter(
        os.path.join(DATA_PATH, ruta_salida),
        engine="openpyxl", 
    ) as writer:
        entidades.to_excel(writer, sheet_name="Top_30_Entidades", index=False)
        macro.to_excel(writer, sheet_name="Top_10_Por_Categoría", index=False)
        entidad_macro_sub.to_excel(writer, sheet_name="Top_10_Por_Subcategoría", index=False)

nacional = pd.read_excel(os.path.join(DATA_PATH, "SECOP_CAT_nacional.xlsx"))
contratos(nacional, "Contratos_nacional.xlsx")

territorial = pd.read_excel(os.path.join(DATA_PATH, "SECOP_CAT_territorio.xlsx"))
contratos(territorial, "Contratos_territorio.xlsx")
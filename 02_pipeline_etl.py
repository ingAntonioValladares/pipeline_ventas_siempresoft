import os
import glob
import pandas as pd
from config import RUTA_DRIVE_BASE, ANIOS_PROCESAR, DIR_REPORTES

MESES_VALIDOS = [
    'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
    'JULIO', 'AGOSTO', 'SETIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'
]

def procesar_archivo_ventas(ruta_archivo, anio):
    df_raw = pd.read_excel(ruta_archivo, header=None)

    # 1. Buscar la fila cabecera de meses
    fila_meses_idx = None
    for idx, row in df_raw.iterrows():
        valores_cadena = [str(val).strip().upper() for val in row.values]
        if 'ENERO' in valores_cadena and 'FEBRERO' in valores_cadena:
            fila_meses_idx = idx
            break

    if fila_meses_idx is None:
        print(f"⚠️ No se encontró la cabecera de meses en {os.path.basename(ruta_archivo)}")
        return pd.DataFrame()

    # 2. Extraer datos y mapear columnas por posición fija de Excel
    df_data = df_raw.iloc[fila_meses_idx + 1:].copy()

    mapa_columnas = {
        0: 'COD_CLIENTE',
        1: 'CLIENTE',
        5: 'COD_ARTICULO',
        7: 'ARTICULO',
        13: 'UM',
        14: 'METRICA'
    }

    fila_meses_series = df_raw.iloc[fila_meses_idx]
    for col_idx, valor in fila_meses_series.items():
        val_str = str(valor).strip().upper()
        if val_str in MESES_VALIDOS:
            mapa_columnas[col_idx] = val_str

    cols_existentes = [c for c in mapa_columnas.keys() if c in df_data.columns]
    df_data = df_data[cols_existentes].rename(columns=mapa_columnas)

    # 3. Filtrar únicamente filas con métrica válida
    df_data['METRICA'] = df_data['METRICA'].astype(str).str.strip().str.upper()
    df_data = df_data[df_data['METRICA'].isin(['CANTIDAD', 'IMPORTE'])].copy()

    # 4. Marcar explícitamente las filas que dicen "Sub Total" ANTES de rellenar
    es_subtotal_raw = (
        df_data['COD_ARTICULO'].astype(str).str.contains('Sub Total|SubTotal|Total', case=False, na=False) |
        df_data['ARTICULO'].astype(str).str.contains('Sub Total|SubTotal|Total', case=False, na=False)
    )

    # 5. Propagar (ffill) Cliente, Código, Artículo y UM a las sub-filas de IMPORTE
    df_data['COD_CLIENTE'] = df_data['COD_CLIENTE'].ffill()
    df_data['CLIENTE'] = df_data['CLIENTE'].ffill()
    df_data['COD_ARTICULO'] = df_data['COD_ARTICULO'].ffill()
    df_data['ARTICULO'] = df_data['ARTICULO'].ffill()
    df_data['UM'] = df_data['UM'].ffill()

    # 6. Descartar filas marcadas como Sub Total y validar que COD_ARTICULO sea numérico
    cod_numerico = pd.to_numeric(df_data['COD_ARTICULO'], errors='coerce')
    es_producto_valido = (~es_subtotal_raw) & (cod_numerico.notna())

    df_data = df_data[es_producto_valido].copy()

    if df_data.empty:
        return pd.DataFrame()

    df_data['COD_ARTICULO'] = cod_numerico[es_producto_valido].astype(int)

    # 7. Unpivot / Melt
    cols_id = [c for c in ['COD_CLIENTE', 'CLIENTE', 'COD_ARTICULO', 'ARTICULO', 'UM', 'METRICA'] if c in df_data.columns]
    cols_meses_presentes = [m for m in MESES_VALIDOS if m in df_data.columns]

    df_melted = df_data.melt(
        id_vars=cols_id,
        value_vars=cols_meses_presentes,
        var_name='MES',
        value_name='VALOR'
    )

    df_melted['VALOR'] = pd.to_numeric(df_melted['VALOR'], errors='coerce').fillna(0.0)
    df_melted = df_melted[df_melted['VALOR'] != 0].copy()

    if df_melted.empty:
        return pd.DataFrame()

    # 8. Pivot para consolidar CANTIDAD e IMPORTE en columnas independientes
    idx_pivot = [c for c in ['COD_CLIENTE', 'CLIENTE', 'COD_ARTICULO', 'ARTICULO', 'UM', 'MES'] if c in df_melted.columns]
    
    df_pivot = df_melted.pivot_table(
        index=idx_pivot,
        columns='METRICA',
        values='VALOR',
        aggfunc='sum'
    ).reset_index()

    if 'CANTIDAD' not in df_pivot.columns: df_pivot['CANTIDAD'] = 0.0
    if 'IMPORTE' not in df_pivot.columns: df_pivot['IMPORTE'] = 0.0

    df_pivot['ANIO'] = int(anio)
    df_pivot = df_pivot.fillna(0.0)

    cols_finales = ['ANIO', 'MES', 'COD_CLIENTE', 'CLIENTE', 'COD_ARTICULO', 'ARTICULO', 'UM', 'CANTIDAD', 'IMPORTE']
    cols_existentes_finales = [c for c in cols_finales if c in df_pivot.columns]
    
    return df_pivot[cols_existentes_finales]

def ejecutar_pipeline():
    print("=" * 70)
    print("  EJECUTANDO PIPELINE ETL DE VENTAS (CANTIDAD E IMPORTE CORREGIDOS)")
    print("=" * 70 + "\n")

    lista_df = []

    for anio in ANIOS_PROCESAR:
        ruta_subcarpeta = os.path.join(RUTA_DRIVE_BASE, anio)
        patron = os.path.join(ruta_subcarpeta, f"*VENTAS POR CLIENTE ARTICULO*{anio}*.xlsx")
        archivos = glob.glob(patron)
        if not archivos:
            archivos = glob.glob(os.path.join(ruta_subcarpeta, "*CLIENTE*ARTICULO*.xlsx"))

        for archivo in archivos:
            print(f"⏳ Procesando año {anio}: {os.path.basename(archivo)}...")
            df_proc = procesar_archivo_ventas(archivo, anio)
            if not df_proc.empty:
                lista_df.append(df_proc)
                print(f"   ✓ Registros puros de detalle: {len(df_proc):,}")
            else:
                print(f"   ⚠️ No se extrajeron filas para {anio}.")

    if lista_df:
        df_consolidado = pd.concat(lista_df, ignore_index=True)
        
        os.makedirs(DIR_REPORTES, exist_ok=True)
        ruta_salida_csv = os.path.join(DIR_REPORTES, "consolidado_ventas_siempresoft.csv")
        ruta_salida_excel = os.path.join(DIR_REPORTES, "consolidado_ventas_siempresoft.xlsx")

        df_consolidado.to_csv(ruta_salida_csv, index=False, encoding='utf-8-sig')
        df_consolidado.to_excel(ruta_salida_excel, index=False)

        print("\n" + "=" * 70)
        print("  ✅ PIPELINE FINALIZADO CON ÉXITO")
        print("=" * 70)
        print(f" Total de registros puros (Nivel Ítem): {len(df_consolidado):,}")
        print(f" 📂 Archivo CSV generado: {ruta_salida_csv}")
        print(f" 📂 Archivo Excel generado: {ruta_salida_excel}")
        print("=" * 70)

if __name__ == "__main__":
    ejecutar_pipeline()
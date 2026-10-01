import os
import glob
import pandas as pd
from config import RUTA_DRIVE_BASE, ANIOS_PROCESAR

def inspeccionar_encabezados_reales():
    print("=" * 70)
    print("  AUDITORÍA DE ENCABEZADOS REALES - SIEMPRESOFT")
    print("=" * 70 + "\n")

    for anio in ANIOS_PROCESAR:
        ruta_subcarpeta = os.path.join(RUTA_DRIVE_BASE, anio)
        print(f"\n📂 AÑO: {anio}")
        
        # Enfocarnos en el archivo más completo: VENTAS POR CLIENTE ARTICULO
        patron = os.path.join(ruta_subcarpeta, f"*VENTAS POR CLIENTE ARTICULO*{anio}*.xlsx")
        archivos = glob.glob(patron)
        
        if not archivos:
            # Si no hace match exacto por nombre, busca cualquier archivo que contenga CLIENTE ARTICULO
            patron_alt = os.path.join(ruta_subcarpeta, "*CLIENTE*ARTICULO*.xlsx")
            archivos = glob.glob(patron_alt)

        for archivo_path in archivos:
            nombre = os.path.basename(archivo_path)
            print(f"📄 Inspeccionando: {nombre}")
            
            # Probar saltar filas (skiprows) para ubicar el encabezado real de datos
            for skip in [3, 4, 5, 6]:
                try:
                    df = pd.read_excel(archivo_path, skiprows=skip, nrows=3)
                    cols_validas = [str(c).strip() for c in df.columns if not str(c).startswith('Unnamed')]
                    
                    if len(cols_validas) > 3:  # Si encontramos varios nombres de columnas reconocibles
                        print(f"   ✅ Encabezado detectado en fila/saltando {skip} filas:")
                        for idx, col in enumerate(df.columns, 1):
                            val_sample = df.iloc[0, idx-1] if len(df) > 0 else ""
                            print(f"      {idx:02d}. [{col}] -> Muestra: {val_sample}")
                        break
                except Exception as e:
                    continue
            print("-" * 60)

if __name__ == "__main__":
    inspeccionar_encabezados_reales()
import os

# ----------------------------------------------------------------------
# RUTA PRINCIPAL A GOOGLE DRIVE
# Cambia esta ruta por la ubicación real del acceso directo en tu disco G:\
# Ejemplo: r"G:\Mi unidad\Ventas_Siempresoft"
# ----------------------------------------------------------------------
RUTA_DRIVE_BASE = r"G:\.shortcut-targets-by-id\1qcto8p4HdZT5RSQB9dAvVJLl3_oodRRN\REPORTES AGSM"

# Años a procesar en el pipeline
ANIOS_PROCESAR = ['2024', '2025', '2026']

# Directorio local dentro del proyecto para guardar los reportes de salida
DIR_REPORTES = "reportes"
os.makedirs(DIR_REPORTES, exist_ok=True)
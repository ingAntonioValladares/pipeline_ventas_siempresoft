# 📊 Pipeline ETL de Ventas - SiempreSoft / AlwaysData

Pipeline de Extracción, Transformación y Carga (ETL) automatizado en Python para el procesamiento, limpieza y consolidación de reportes de ventas matriciales del ERP SiempreSoft (período 2024–2026), garantizando un 100% de integridad de datos para modelos analíticos en Power BI.

---

## 🛠️️ Problema Técnico Resuelto

Los reportes exportados en formato Excel desde SiempreSoft presentan inconsistencias estructurales complejas:

1. **Encabezados desplazados y celdas combinadas verticalmente.**
2. **Duplicación de filas de métricas (`CANTIDAD` e `IMPORTE`).**
3. **Filas de "Sub Total" intercaladas**, que provocaban doble contabilización de importes y pérdida del código de artículo en las subfilas.

### 💡 Solución Implementada (`02_pipeline_etl.py`)

- **Propagación de Contexto:** Aplicación de `ffill()` a nivel de cliente y código de artículo previo a la extracción de métricas.
- **Filtrado Riguroso de Subtotales:** Remoción de filas resúmenes antes de la asignación de métricas.
- **Unificación de Métricas:** Normalización de la estructura matricial mensual (Enero–Diciembre) a un modelo de grano a nivel de ítem.

---

## 📂 Estructura del Repositorio

```text
pipeline_ventas_siempresoft/
│
├── 01_auditoria_archivos.py    # Script de diagnóstico estructural e inspección de hojas Excel
├── 02_pipeline_etl.py          # Pipeline principal de consolidación y limpieza
├── config.py                   # Configuración de rutas, nombres de archivos y parámetros
├── requirements.txt            # Dependencias del proyecto
├── INSTRUCCIONES_CARGA.txt     # Guía operativa para cargas periódicas (diarias/semanales/mensuales)
└── .gitignore                  # Exclusión de entornos virtuales, cachés y reportes locales
```

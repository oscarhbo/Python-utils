import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import random

# Datos de ejemplo
data = {
    'columna1': [random.choice(['A', 'B', 'C']) for _ in range(30)],
    'columna2': [random.randint(1, 10) for _ in range(30)],
    'columna3': [random.choice(['X', 'Y', 'Z']) for _ in range(30)],
    'valor': [random.uniform(1.0, 100.0) for _ in range(30)],
}

df = pd.DataFrame(data)

tabla_arrow = pa.table(df)

ruta_directorio_parquet = 'D:\Repositorios\Git\Python-utils\\big_data\contenedor\poc_particion'

columnas_particion = ['columna1', 'columna2']

compresion = None

pq.write_to_dataset(tabla_arrow, root_path=ruta_directorio_parquet, partition_cols=columnas_particion, compression=compresion)

print(f"Archivos Parquet particionados sin compresión en: {ruta_directorio_parquet}")

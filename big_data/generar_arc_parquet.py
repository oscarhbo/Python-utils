import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import random

# Datos de ejemplo random
data = {
    'columna1': [random.randint(1, 100) for _ in range(10)],
    'columna2': [random.uniform(1.0, 10.0) for _ in range(10)],
    'columna3': [random.choice(['A', 'B', 'C']) for _ in range(10)],
    'columna4': [random.random() > 0.5 for _ in range(10)],
    'columna5': pd.date_range('2022-01-01', periods=10, freq='D'),
    'columna6': [f'Texto-{i}' for i in range(10)],
    'columna7': [None if random.random() > 0.8 else random.randint(1, 100) for _ in range(10)],
    'columna8': [random.choice([True, False, None]) for _ in range(10)]
}

df = pd.DataFrame(data)

tabla_arrow = pa.table(df)

ruta_archivo_parquet = 'D:\Repositorios\Git\Python-utils\\big_data\contenedor\muestra.parquet'

pq.write_table(tabla_arrow, ruta_archivo_parquet)

print(f"Archivo Parquet generado con éxito en: {ruta_archivo_parquet}")

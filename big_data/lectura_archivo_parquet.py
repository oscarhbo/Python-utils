import pandas as pd
import pyarrow.parquet as pq

#archivo_parquet_local = "D:\\tmp\muestras\Spark_Bluetab\contracts\ExpectedMP.parquet"
#archivo_parquet_local = "D:\Repositorios\Git\spark-essentials\src\main\\resources\data\movies_parquet"
archivo_parquet_local = 'D:\Repositorios\Git\Python-utils\\big_data\contenedor\muestra.parquet'

archivo_parquet_local = 'D:\Repositorios\Git\Python-utils\\big_data\contenedor\poc_particion'
print(archivo_parquet_local)

tabla_parquet = pq.read_table(archivo_parquet_local)

df = tabla_parquet.to_pandas()


nombres_de_columnas = df.columns
print("Nombres de las columnas:", nombres_de_columnas)

df.info

print(df.head(10))


import pyarrow.parquet as pq
import pandas as pd 


rutaBase = "d:\\Repositorios\\Git\\Python-utils\\tmp\\"

def leer_parquet(ruta_archivo_parquet):
    print(f"se leera el archivo {ruta_archivo_parquet}")

    try:
        
        pq_file = pq.ParquetFile(ruta_archivo_parquet)

        print("\nMetadatos del archivo Parquet:")
        print(pq_file.metadata)

        print("\nMetadatos del esquema:")
        print(pq_file.schema_arrow.metadata)

        table = pq.read_table(ruta_archivo_parquet)

 
        print("\nMuestra del Archivo:\n")
        print(table.to_pandas().head())
        
    except Exception as e:
        print(f" [Error] al leer archivo parquet - {str(e)}")    


leer_parquet(rutaBase + "ejemplo_emp.snappy.parquet" )
import pandas as pd
import chardet

rutaBase = "d:\\Repositorios\\Git\\Python-utils\\tmp\\"

def detect_encoding(file_path):
    """
    Detectar el encoding de un archivo.
    
    Parametros:
    file_path (str): La ruta del archivo a verificar.
    
    Returns:
    str: El encoding cetectado.
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    return encoding


def ConvertCsvToParquet(ruta_archivo_csv,   ruta_archivo_parquet):
    
    print(f"Se generará el archivo parquet {ruta_archivo_parquet} a partir del archivo {ruta_archivo_csv}")

    try:
        encoding_archivo = detect_encoding(ruta_archivo_csv)
        df = pd.read_csv(ruta_archivo_csv, encoding=encoding_archivo)

        num_regs, num_cols = df.shape

        print(f"El Archivo tiene {num_regs} registros y tiene {num_cols} columnas.\n")

        print("se pintará una muestra de la información\n")

        print(df.head())

        #df.to_parquet(ruta_archivo_parquet, engine='pyarrow', index=False)
        df.to_parquet(ruta_archivo_parquet, engine='pyarrow', compression='snappy', index=False)


    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}" )    

    
ConvertCsvToParquet(rutaBase + "ejemplo_emp.csv",  rutaBase + "ejemplo_emp.snappy.parquet")



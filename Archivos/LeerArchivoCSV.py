import csv

rutaDir = "d:\\Repositorios\\Git\\Python-utils\\tmp\\"

def leerArchivoCsv(NombreArchivo):
    print(f"Inicia lectura de archivo csv: {NombreArchivo}" )
    print('-' * 100)
    
    with open(NombreArchivo, mode='r', ) as archivo:
        lector = csv.reader(archivo)

        Header = next(lector)

        print("Cabeceros: " , Header) # se puede mostrar como una lista
        print("Cabeceros: " , ','.join(Header)) # o se puede mostrar como una línea de texto

        for linea in lector:
            print(','.join(linea))


    print('-' * 100)
    print(f"Finaliza la lectura del archivo: {NombreArchivo}")

leerArchivoCsv(rutaDir + "ejemplo_emp.csv")
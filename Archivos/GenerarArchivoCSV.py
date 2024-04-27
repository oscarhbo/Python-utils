import csv

rutaDir = "d:\\Repositorios\\Git\\Python-utils\\tmp\\"

def generarArchivoCsv(NombreArchivo):
    print(f"Inicia generación de archivo csv: {NombreArchivo}" )
    
    Header=["IdEmpleado", "NombreEmpleado", "FechaNacimiento", "Género"]
    Datos=[
            ["1","Juan Jose Villa de la Peña","01/01/1995","M"],
            ["2","Karla Pérez Zuñiga","02/03/1999","F"],
            ["3","Rocio Rosales Villada","30/11/1998","F"],
            ["4","Carlos Plasencia Najera","01/01/2000","M"],
          ] 

    with open(NombreArchivo, mode='w', newline='') as archivo:
        escritor = csv.writer(archivo, delimiter=',')

        escritor.writerow(Header)
        escritor.writerows(Datos)

    print(f"Finaliza la creación del archivo: {NombreArchivo}")

generarArchivoCsv(rutaDir + "ejemplo_emp.csv")
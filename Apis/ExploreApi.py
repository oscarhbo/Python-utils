from ast import For
import requests
import json



def Format_Json(pData):
    print(json.dumps(pData, indent=4))
    #print(pData)

def ExecRequest(pUrl):

    r = requests.get(url)

    print(r.status_code)

    print('El código de respuesta de la peticion es: {}'.format( r.status_code))

    json_respuesta = r.json()
    nombre = json_respuesta['name']
    status = json_respuesta['status']

    print('El nombre del personaje es {} y su estatus es {}'.format(nombre,status))


"""
for i in range(1,10):

    url = 'https://rickandmortyapi.com/api/character/{}'.format(i)
    ExecRequest(url)
"""

print(' --------------------------------------------------')
print(' --            Salida del json Indentado         --')
print(' --------------------------------------------------')


url='https://rickandmortyapi.com/api/character/1'

r = requests.get(url)
j = r.json()

Format_Json(j)


print(' --------------------------------------------------')
print(' --      Imprimir todas las llaves del json      --')
print(' --------------------------------------------------')
llaves = j.keys() 
print(type(llaves))

for llave in llaves:
    print('El valor para la llave {}, es {}'.format(llave, j[llave]))


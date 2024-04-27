nombre = input("Por favor, ingresa tu nombre: ")
edad = int(input("Por favor, ingresa tu edad: "))
le_gusta_videojuegos = input("¿Te gusta jugar videojuegos? (sí/no): ")

mensaje = f"Hola, {nombre}! Tienes {edad} años y "
if le_gusta_videojuegos.lower() == "sí":
    mensaje += "te gusta jugar videojuegos."
else:
    mensaje += "no te gusta jugar videojuegos."

print(mensaje)

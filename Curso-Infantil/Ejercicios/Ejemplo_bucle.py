# Ejemplo de bucle en Python

# Bucle for que itera sobre una secuencia de números del 1 al 5

print("Inicia el programa")

for contador in range(1, 11, 1):
    print("TABLA DEL " + str(contador)) 
    print("------------------------")
    for x in range(1, 11, 1):    
        print(str(contador) + " * "+ str(x) + " = ", contador * x )

    print(" ")

# Fin del programa
print("Fin del programa")

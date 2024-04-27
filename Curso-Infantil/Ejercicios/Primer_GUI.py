import tkinter as tk

def saludar():
    nombre = entrada_nombre.get()
    mensaje_saludo.set(f"Hola, {nombre}, ¿cómo estás?")


ventana = tk.Tk()
ventana.title("Saludo v1")


mensaje_saludo = tk.StringVar()


etiqueta_nombre = tk.Label(ventana, text="Nombre:")
etiqueta_nombre.pack(pady=10)

entrada_nombre = tk.Entry(ventana)
entrada_nombre.pack(pady=10)

boton_saludo = tk.Button(ventana, text="Saludo", command=saludar)
boton_saludo.pack(pady=10)

etiqueta_resultado = tk.Label(ventana, textvariable=mensaje_saludo)
etiqueta_resultado.pack(pady=10)


ventana.geometry("400x200")


ventana.mainloop()
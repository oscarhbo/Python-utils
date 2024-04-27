import tkinter as tk
from tkinter import messagebox

def mostrar_mensaje():
    nombre = entry_nombre.get()
    edad = entry_edad.get()
    le_gusta_videojuegos = variable_videojuegos.get()

    mensaje = f"Hola, {nombre}! Tienes {edad} años y "
    if le_gusta_videojuegos == "sí":
        mensaje += "te gusta jugar videojuegos."
    else:
        mensaje += "no te gusta jugar videojuegos."

    messagebox.showinfo("Mensaje personalizado", mensaje)

app = tk.Tk()
app.title("Saludo personalizado")

frame = tk.Frame(app)
frame.pack(padx=20, pady=20)

label_nombre = tk.Label(frame, text="Por favor, ingresa tu nombre:")
label_nombre.grid(row=0, column=0, sticky="e")
entry_nombre = tk.Entry(frame)
entry_nombre.grid(row=0, column=1)

label_edad = tk.Label(frame, text="Por favor, ingresa tu edad:")
label_edad.grid(row=1, column=0, sticky="e")
entry_edad = tk.Entry(frame)
entry_edad.grid(row=1, column=1)

label_videojuegos = tk.Label(frame, text="¿Te gusta jugar videojuegos?")
label_videojuegos.grid(row=2, column=0, sticky="e")
variable_videojuegos = tk.StringVar(frame)
variable_videojuegos.set("sí")
opciones = ("sí", "no")
menu_desplegable = tk.OptionMenu(frame, variable_videojuegos, *opciones)
menu_desplegable.grid(row=2, column=1)

boton = tk.Button(frame, text="Mostrar mensaje", command=mostrar_mensaje)
boton.grid(row=3, columnspan=2, pady=10)

app.mainloop()

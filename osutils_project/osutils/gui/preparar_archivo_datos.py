import customtkinter as ctk
from tkinter import filedialog
from datetime import datetime
import os

class PrepararArchivoDatosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=10, padx=30, fill="both", expand=True)

        # Instrucción inicial
        ctk.CTkLabel(content_frame, text="Seleccione el archivo de datos a ajustar.", font=("Arial", 14), anchor="w").pack(pady=(0, 10), anchor="w")

        # Selector de archivo
        file_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        file_row.pack(pady=10, fill="x")
        self.file_entry = ctk.CTkEntry(file_row, width=500)
        self.file_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
        self.btn_explorar = ctk.CTkButton(file_row, text="📂", width=40, height=28, command=self.seleccionar_archivo)
        self.btn_explorar.pack(side="left")

        # Muestra original
        ctk.CTkLabel(content_frame, text="Primeros 5 registros del archivo original:", anchor="w").pack(pady=(5, 0), anchor="w")
        self.muestra_original = ctk.CTkTextbox(content_frame, height=100, width=700)
        self.muestra_original.pack(pady=5, anchor="w", fill="x")

        # Botón para ajustar archivo
        self.btn_ajustar = ctk.CTkButton(content_frame, text="Ajustar archivo", command=self.ajustar_archivo)
        self.btn_ajustar.pack(pady=10, anchor="w")

        # Muestra ajustada
        ctk.CTkLabel(content_frame, text="Primeros 5 registros del archivo ajustado:", anchor="w").pack(pady=(5, 0), anchor="w")
        self.muestra_ajustada = ctk.CTkTextbox(content_frame, height=100, width=700)
        self.muestra_ajustada.pack(pady=5, anchor="w", fill="x")

        # Mensaje de estado
        self.mensaje = ctk.CTkLabel(content_frame, text="", font=("Arial", 13))
        self.mensaje.pack(pady=5, anchor="w")

        self.archivo_actual = None
        self.archivo_ajustado = None

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(title="Selecciona el archivo de datos", filetypes=[("Archivos de texto", "*.txt;*.csv"), ("Todos", "*.*")])
        if ruta:
            self.archivo_actual = ruta
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, ruta)
            self.muestra_original.delete("1.0", "end")
            with open(ruta, "r", encoding="utf-8") as f:
                for i, linea in enumerate(f):
                    if i >= 5:
                        break
                    self.muestra_original.insert("end", linea)
            self.muestra_ajustada.delete("1.0", "end")
            self.archivo_ajustado = None

    def ajustar_archivo(self):
        if not self.archivo_actual:
            self.muestra_ajustada.delete("1.0", "end")
            self.muestra_ajustada.insert("end", "Selecciona primero un archivo de datos.")
            self.mensaje.configure(text="")
            return
        ruta = self.archivo_actual
        base, ext = os.path.splitext(ruta)
        nuevo_nombre = base + "_ok" + ext
        hoy = datetime.now().strftime("%d/%m/%Y")
        lineas_ajustadas = []
        error_formato = False
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                linea_strip = linea.strip()
                if not linea_strip:
                    continue
                if not linea_strip[0].isalpha():
                    error_formato = True
                    break
                partes = linea_strip.split(",")
                if len(partes) < 3:
                    continue  # línea inválida
                nueva = partes[2:] + [hoy, ""]
                lineas_ajustadas.append(",".join(nueva))
        if error_formato:
            self.muestra_ajustada.delete("1.0", "end")
            self.mensaje.configure(text="❌ El archivo a ajustar no tiene el formato esperado: hay líneas que no inician con letras.")
            return
        with open(nuevo_nombre, "w", encoding="utf-8") as f:
            for l in lineas_ajustadas:
                f.write(l + "\n")
        self.archivo_ajustado = nuevo_nombre
        # Mostrar muestra
        self.muestra_ajustada.delete("1.0", "end")
        for l in lineas_ajustadas[:5]:
            self.muestra_ajustada.insert("end", l + "\n")
        self.mensaje.configure(text=f"✅ Archivo ajustado correctamente: {os.path.basename(nuevo_nombre)}")

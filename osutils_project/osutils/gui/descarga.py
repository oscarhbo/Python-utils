import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from osutils.gui.conexion import SelectorConexionOracle
from osutils.db.oracle import obtener_paquete_oracle

class DescargarPaqueteFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=10, padx=30, fill="both", expand=True)
        self.selector = SelectorConexionOracle(content_frame, on_change=self.on_conexion_cambiada)
        self.selector.pack(pady=10, anchor="w")
        ctk.CTkLabel(content_frame, text="Nombre del paquete:", anchor="w").pack(pady=5, anchor="w")
        self.package_entry = ctk.CTkEntry(content_frame, width=320)
        self.package_entry.pack(pady=5, anchor="w")
        self.package_entry.bind("<KeyRelease>", self.on_keyrelease)
        self.listbox = tk.Listbox(content_frame, height=5)
        self.listbox.pack(pady=0, fill="x", anchor="w")
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)
        self.listbox.pack_forget()
        ruta_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        ruta_frame.pack(pady=5, anchor="w")
        self.path_entry = ctk.CTkEntry(ruta_frame, width=320)
        self.path_entry.pack(side="left", padx=(0, 5))
        self.btn_explorar = ctk.CTkButton(
            ruta_frame,
            text="📂",
            width=40,
            height=28,
            command=self.seleccionar_ruta
        )
        self.btn_explorar.pack(side="left")
        ctk.CTkLabel(content_frame, text="Ruta de guardado (incluye nombre_archivo.sql):").pack(pady=5, anchor="w")
        ctk.CTkButton(content_frame, text="Descargar paquete", command=self.descargar).pack(pady=20, anchor="w")
        self.mensaje = ctk.CTkLabel(content_frame, text="", font=("Arial", 14))
        self.mensaje.pack(pady=10, anchor="w")
        self.paquetes = []
    def on_conexion_cambiada(self, conexion_seleccionada):
        self.mensaje.configure(text=f"Cargando paquetes para {conexion_seleccionada}...")
        self.obtener_lista_paquetes()
    def obtener_lista_paquetes(self):
        try:
            connection = self.selector.connect()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT object_name FROM all_objects
                WHERE object_type = 'PACKAGE' AND owner = 'GORAPR'
                ORDER BY object_name
            """)
            self.paquetes = [row[0] for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            self.mensaje.configure(text=f"Lista de paquetes cargada ({len(self.paquetes)})")
        except Exception as e:
            self.mensaje.configure(text=f"❌ Error al obtener lista de paquetes: {str(e)}")
    def on_keyrelease(self, event):
        texto = self.package_entry.get().upper()
        if texto == "":
            self.listbox.pack_forget()
            return
        coincidencias = [p for p in self.paquetes if texto in p]
        if coincidencias:
            self.listbox.delete(0, "end")
            for item in coincidencias:
                self.listbox.insert("end", item)
            self.listbox.pack(pady=0, fill="x")
        else:
            self.listbox.pack_forget()
    def on_listbox_select(self, event):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        valor = self.listbox.get(index)
        self.package_entry.delete(0, "end")
        self.package_entry.insert(0, valor)
        self.listbox.pack_forget()
    def seleccionar_ruta(self):
        nombre_paquete = self.package_entry.get().strip().upper()
        if not nombre_paquete:
            self.mensaje.configure(text="⚠️ Ingresa el nombre del paquete primero.")
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql")],
            initialfile=f"{nombre_paquete}.sql",
            title="Selecciona dónde guardar el paquete"
        )
        if ruta:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, ruta)
    def descargar(self):
        nombre_paquete = self.package_entry.get().strip().upper()
        ruta_salida = self.path_entry.get().strip()
        if not nombre_paquete or not ruta_salida:
            self.mensaje.configure(text="⚠️ Llena todos los campos antes de descargar.")
            return
        try:
            connection = self.selector.connect()
            codigo = obtener_paquete_oracle(nombre_paquete, connection)
            with open(ruta_salida, "w", encoding="ansi") as f:
                f.write(codigo)
            self.mensaje.configure(text=f"✅ Paquete {nombre_paquete} guardado correctamente")
            connection.close()
        except Exception as e:
            self.mensaje.configure(text=f"❌ Error: {str(e)}")

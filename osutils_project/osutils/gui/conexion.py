import customtkinter as ctk
import configparser
import os
import sys
from tkinter import messagebox
from osutils.db.oracle import OracleConnectionManager


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INI_PATH = os.path.join(PROJECT_ROOT, "db_connections.ini")

class SelectorConexionOracle(ctk.CTkFrame):
    def __init__(self, master, config_ini_path=INI_PATH, on_change=None, bg_color=None):
        fg_color = bg_color if bg_color not in (None, "transparent") else None
        if fg_color:
            super().__init__(master, fg_color=fg_color)
        else:
            super().__init__(master)
        self.config = configparser.ConfigParser()
        self.config.read(config_ini_path)
        self.conexiones = self.config.sections()
        self.on_change = on_change
        label_fg_color = bg_color if bg_color not in (None, "transparent") else None
        if label_fg_color:
            self.label = ctk.CTkLabel(self, text="Selecciona una conexión", font=("Arial", 14), fg_color=label_fg_color)
        else:
            self.label = ctk.CTkLabel(self, text="Selecciona una conexión", font=("Arial", 14))
        self.label.pack(pady=5, anchor="w")
        # No pasar fg_color a CTkOptionMenu, solo usar valores y command
        self.combo = ctk.CTkOptionMenu(self, values=self.conexiones, command=self._on_select)
        self.combo.pack(pady=5, anchor="w")
        if self.conexiones:
            self.combo.set(self.conexiones[0])
    def _on_select(self, value):
        if self.on_change:
            self.on_change(value)
    def get_selected(self):
        return self.combo.get()
    def connect(self):
        try:
            return OracleConnectionManager.connect(self.config, self.get_selected())
        except RuntimeError as e:
            if "Oracle Client library ya fue inicializado" in str(e):
                messagebox.showwarning(
                    "Reinicio requerido",
                    "Se requiere reiniciar la aplicación para cambiar de tipo de conexión (local/cloud). La app se reiniciará automáticamente."
                )
                self.after(1000, reiniciar_aplicacion)
                raise
            else:
                raise

def reiniciar_aplicacion():
    python = sys.executable
    os.execl(python, python, *sys.argv)

class ConexionOracleFrame(ctk.CTkFrame):
    def __init__(self, master, bg_color=None):
        super().__init__(master)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=10, padx=30, fill="both", expand=True)
        # Frame horizontal para selector y botón
        top_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_row.pack(pady=10, fill="x")
        self.selector = SelectorConexionOracle(top_row, bg_color=bg_color)
        self.selector.pack(side="left", anchor="w")
        self.boton = ctk.CTkButton(top_row, text="Probar conexión", command=self.probar_conexion, width=160)
        self.boton.pack(side="right", anchor="e", padx=(10, 0))
        self.resultado = ctk.CTkTextbox(content_frame, height=100, width=700)
        self.resultado.pack(pady=10, anchor="w", fill="x")
        # --- NUEVO: Caja de texto para query SQL ---
        ctk.CTkLabel(content_frame, text="Consulta rápida (Ctrl+Enter para ejecutar):", anchor="w").pack(pady=(10, 0), anchor="w")
        self.query_text = ctk.CTkTextbox(content_frame, height=80, width=700)
        self.query_text.pack(pady=5, anchor="w", fill="x")
        self.query_text.bind("<Control-Return>", self.ejecutar_query_event)
        # --- NUEVO: Caja de texto para resultado de query ---
        ctk.CTkLabel(content_frame, text="Resultado de la consulta:", anchor="w").pack(pady=(10, 0), anchor="w")
        self.query_result = ctk.CTkTextbox(content_frame, height=120, width=700)
        self.query_result.pack(pady=5, anchor="w", fill="x")
    def probar_conexion(self):
        self.resultado.delete("1.0", "end")
        try:
            connection = self.selector.connect()
            self.resultado.insert("end", f"✅ Conexión exitosa a {self.selector.get_selected()}\n")
            self.resultado.insert("end", f"Versión del servidor: {connection.version}\n\n")
            connection.close()
        except Exception as e:
            self.resultado.insert("end", f"❌ Error: {str(e)}\n\n")
    def ejecutar_query_event(self, event=None):
        self.ejecutar_query()
        return "break"
    def ejecutar_query(self):
        self.query_result.delete("1.0", "end")
        query = self.query_text.get("1.0", "end").strip()
        if not query.lower().startswith("select"):
            self.query_result.insert("end", "Solo se permiten consultas SELECT para pruebas rápidas.")
            return
        try:
            connection = self.selector.connect()
            cursor = connection.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            # Formatear resultado como tabla simple
            col_line = " | ".join(columns)
            self.query_result.insert("end", col_line + "\n" + ("-" * len(col_line)) + "\n")
            for row in rows:
                self.query_result.insert("end", " | ".join(str(val) for val in row) + "\n")
            cursor.close()
            connection.close()
        except Exception as e:
            self.query_result.insert("end", f"❌ Error: {str(e)}\n")

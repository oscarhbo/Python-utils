import customtkinter as ctk
from osutils.gui.conexion import ConexionOracleFrame
from osutils.gui.descarga import DescargarPaqueteFrame
from osutils.gui.sqlloader import SQLLoaderFrame
from osutils.gui.respaldo_alianza import RespaldoAlianzaFrame
from osutils.gui.descargar_consultas import DescargarConsultasFrame
from osutils.gui.preparar_archivo_datos import PrepararArchivoDatosFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Administrador de Herramientas")
        self.geometry("880x550")

        self.menu_frame = ctk.CTkFrame(self, width=180, fg_color="#2A2A2A")
        self.menu_frame.pack(side="left", fill="y")

        self.main_frame = ctk.CTkFrame(self, fg_color="#ded7d7") 
        self.main_frame.pack(side="right", expand=True, fill="both")

        self.menu_buttons = {}
        self.active_menu = None  

        self.menu_options = [
            ("🔌 Probar conexión", self.show_conexion_frame),
            ("📦 Descargar paquete", self.show_descarga_frame),
            ("🧩 SQL*Loader", self.show_sqlloader_frame),
            ("📝 Preparar archivo de Datos", self.show_preparar_archivo_datos_frame),
            ("📁 Respaldo Alianza", self.show_respaldo_alianza_frame),
            ("📁 Descargar Consultas", self.show_descargar_consultas_frame),
            ("📁 Respaldo PPR", self.show_under_construction),
        ]

        for texto, comando in self.menu_options:
            btn = ctk.CTkButton(
                self.menu_frame,
                text=texto,
                anchor="w",
                width=180,
                fg_color="transparent",
                hover_color="#1e1e1e",
                text_color="#ffffff",
                command=lambda c=comando, t=texto: self.select_menu(t, c)
            )
            btn.pack(pady=5, fill="x", padx=5)
            self.menu_buttons[texto] = btn

        self.current_frame = None
        # Mostrar por defecto la opción 1 (Probar conexión)
        self.show_conexion_frame()
        self.menu_buttons["🔌 Probar conexión"].configure(
            fg_color="#3b8ed0",
            hover_color="#3b8ed0",
            text_color="white"
        )
        self.active_menu = "🔌 Probar conexión"

    def select_menu(self, texto, callback):
        for t, b in self.menu_buttons.items():
            b.configure(
                fg_color="transparent",
                hover_color="#1e1e1e",  
                text_color="#ffffff"
            )
        self.menu_buttons[texto].configure(
            fg_color="#3b8ed0",
            hover_color="#3b8ed0",  
            text_color="white"
        )
        self.active_menu = texto
        callback()

    def clear_main_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_placeholder(self, mensaje):
        self.clear_main_frame()
        placeholder = ctk.CTkLabel(self.main_frame, text=mensaje, font=("Arial", 16))
        placeholder.pack(pady=20)
        self.current_frame = placeholder

    def show_under_construction(self):
        self.show_placeholder("🚧 Esta funcionalidad está en construcción")

    def show_conexion_frame(self):
        self.clear_main_frame()
        self.current_frame = ConexionOracleFrame(self.main_frame)
        self.current_frame.pack(expand=True, fill="both")

    def show_descarga_frame(self):
        self.clear_main_frame()
        self.current_frame = DescargarPaqueteFrame(self.main_frame)
        self.current_frame.pack(expand=True, fill="both")

    def show_sqlloader_frame(self):
        self.clear_main_frame()
        self.current_frame = SQLLoaderFrame(self.main_frame)
        self.current_frame.pack(expand=True, fill="both")

    def show_preparar_archivo_datos_frame(self):
        self.clear_main_frame()
        self.current_frame = PrepararArchivoDatosFrame(self.main_frame)
        self.current_frame.pack(expand=True, fill="both")

    def show_respaldo_alianza_frame(self):
        self.clear_main_frame()
        self.current_frame = RespaldoAlianzaFrame(self.main_frame)
        self.current_frame.pack(expand=True, fill="both")

    def show_descargar_consultas_frame(self):
        self.clear_main_frame()
        self.current_frame = DescargarConsultasFrame(self.main_frame)
        self.current_frame.pack(expand=True, fill="both")

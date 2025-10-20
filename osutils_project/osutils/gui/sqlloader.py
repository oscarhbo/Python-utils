import customtkinter as ctk
from tkinter import filedialog
import configparser
import os
import threading
import subprocess
from osutils.gui.conexion import SelectorConexionOracle
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(sys.argv[0]))

# Ajuste: obtener la ruta absoluta del INI en la raíz del proyecto
SQLLOADER_CONFIG_PATH = os.path.join(get_base_path(), "sqlloader_config.ini")

class SQLLoaderFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=10, padx=30, fill="both", expand=True)
        self.selector = SelectorConexionOracle(content_frame)
        self.selector.pack(pady=10, anchor="w")
        self.sqlloader_path = self.cargar_ruta_sqlloader()
        ruta_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        ruta_frame.pack(pady=5, anchor="w")
        self.sqlloader_entry = ctk.CTkEntry(ruta_frame, width=320)
        self.sqlloader_entry.pack(side="left", padx=(0, 5))
        self.sqlloader_entry.insert(0, self.sqlloader_path or "")
        self.btn_explorar_sqlloader = ctk.CTkButton(
            ruta_frame,
            text="📂",
            width=40,
            height=28,
            command=self.seleccionar_ruta_sqlloader
        )
        self.btn_explorar_sqlloader.pack(side="left")
        ctk.CTkLabel(content_frame, text="Archivo de control (.ctl):").pack(pady=5, anchor="w")
        ctl_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        ctl_frame.pack(pady=5, anchor="w")
        self.ctl_entry = ctk.CTkEntry(ctl_frame, width=320)
        self.ctl_entry.pack(side="left", padx=(0, 5))
        self.btn_explorar_ctl = ctk.CTkButton(
            ctl_frame,
            text="📂",
            width=40,
            height=28,
            command=self.seleccionar_archivo_ctl
        )
        self.btn_explorar_ctl.pack(side="left")
        self.btn_ejecutar = ctk.CTkButton(content_frame, text="Ejecutar SQL*Loader", command=self.ejecutar_sqlloader)
        self.btn_ejecutar.pack(pady=20, anchor="w")
        self.mensaje = ctk.CTkLabel(content_frame, text="", font=("Arial", 14))
        self.mensaje.pack(pady=10, anchor="w")
        self.texto_avance = ctk.CTkTextbox(content_frame, height=200, width=600)
        self.texto_avance.pack(pady=10, anchor="w")
    def cargar_ruta_sqlloader(self):
        if os.path.exists(SQLLOADER_CONFIG_PATH):
            config = configparser.ConfigParser()
            config.read(SQLLOADER_CONFIG_PATH)
            return config.get("SQLLOADER", "sqlloader_path", fallback="")
        return ""
    def guardar_ruta_sqlloader(self, path):
        config = configparser.ConfigParser()
        config["SQLLOADER"] = {"sqlloader_path": path}
        with open(SQLLOADER_CONFIG_PATH, "w") as f:
            config.write(f)
    def seleccionar_ruta_sqlloader(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona el ejecutable de SQL*Loader",
            filetypes=[("Ejecutable", "*.exe" if os.name == "nt" else "*")]
        )
        if ruta:
            self.sqlloader_entry.delete(0, "end")
            self.sqlloader_entry.insert(0, ruta)
            self.guardar_ruta_sqlloader(ruta)
    def seleccionar_archivo_ctl(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona el archivo .ctl",
            filetypes=[("Archivos CTL", "*.ctl")]
        )
        if ruta:
            self.ctl_entry.delete(0, "end")
            self.ctl_entry.insert(0, ruta)
    def ejecutar_sqlloader(self):
        self.mensaje.configure(text="")
        self.texto_avance.delete("1.0", "end")
        sqlloader_path = self.sqlloader_entry.get().strip()
        ctl_path = self.ctl_entry.get().strip()
        conexion_nombre = self.selector.get_selected()
        if not sqlloader_path or not os.path.exists(sqlloader_path):
            self.mensaje.configure(text="❌ Debes seleccionar el ejecutable de SQL*Loader.")
            return
        if not ctl_path or not os.path.exists(ctl_path):
            self.mensaje.configure(text="❌ Debes seleccionar un archivo .ctl válido.")
            return
        if not conexion_nombre:
            self.mensaje.configure(text="❌ Debes seleccionar una conexión.")
            return
        config = self.selector.config[conexion_nombre]
        user = config["user"]
        password = config["password"]
        if config.get("tipo") == "cloud":
            tns = config["tns_alias"]
            conn_str = f"{user}/{password}@{tns}"
        else:
            host = config["host"]
            port = config["port"]
            service_name = config["service_name"]
            conn_str = f"{user}/{password}@//{host}:{port}/{service_name}"
        ctl_filename = os.path.splitext(os.path.basename(ctl_path))[0]
        log_name = f"LOG_CARGA_{conexion_nombre}_{ctl_filename}.log"
        log_path = os.path.join(os.path.dirname(ctl_path), log_name)
        comando = [
            sqlloader_path,
            conn_str,
            f"control={ctl_path}",
            f"log={log_path}"
        ]
        # --- Ajuste para variables de entorno desde el INI ---
        env = os.environ.copy()
        sqlloader_ini = SQLLOADER_CONFIG_PATH
        if os.path.exists(sqlloader_ini):
            config_ini = configparser.ConfigParser()
            config_ini.read(sqlloader_ini)
            if 'SQLLOADER' in config_ini:
                if 'ORACLE_HOME' in config_ini['SQLLOADER']:
                    env['ORACLE_HOME'] = config_ini['SQLLOADER']['ORACLE_HOME']
                if 'PATH' in config_ini['SQLLOADER']:
                    env['PATH'] = config_ini['SQLLOADER']['PATH'] + ';' + env.get('PATH', '')
                if 'NLS_LANG' in config_ini['SQLLOADER']:
                    env['NLS_LANG'] = config_ini['SQLLOADER']['NLS_LANG']
        # --- Fin ajuste ---
        def run_sqlloader():
            try:
                proc = subprocess.Popen(
                    comando,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=os.path.dirname(ctl_path),
                    env=env
                )
                for line in proc.stdout:
                    self.texto_avance.insert("end", line)
                    self.texto_avance.see("end")
                proc.wait()
                if proc.returncode == 0:
                    self.mensaje.configure(text=f"✅ Carga completada. Log: {log_path}")
                else:
                    self.mensaje.configure(text=f"❌ Error en SQL*Loader. Revisa el log.")
            except Exception as e:
                self.mensaje.configure(text=f"❌ Error al ejecutar SQL*Loader: {str(e)}")
        threading.Thread(target=run_sqlloader, daemon=True).start()

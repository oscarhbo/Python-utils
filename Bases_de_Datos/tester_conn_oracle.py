import customtkinter as ctk
import cx_Oracle
import configparser
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INI_PATH = os.path.join(BASE_DIR, "db_connections.ini")

config = configparser.ConfigParser()
config.read(INI_PATH)
CONEXIONES_DISPONIBLES = config.sections()


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Probador de Conexiones Oracle")
        self.geometry("500x300")

        self.label_titulo = ctk.CTkLabel(self, text="Selecciona una conexión", font=("Arial", 18))
        self.label_titulo.pack(pady=10)

        self.combo = ctk.CTkOptionMenu(self, values=CONEXIONES_DISPONIBLES)
        self.combo.pack(pady=10)

        self.boton = ctk.CTkButton(self, text="Probar conexión", command=self.probar_conexion)
        self.boton.pack(pady=10)

        self.resultado = ctk.CTkTextbox(self, height=100, width=400)
        self.resultado.pack(pady=10)

    def probar_conexion(self):
        nomconexion = self.combo.get()
        if nomconexion not in config:
            self.resultado.insert("end", f"❌ Conexión '{nomconexion}' no encontrada\n")
            return

        conexion = config[nomconexion]
        
        try:
            if conexion.get("tipo") == "cloud":
                wallet_dir = conexion["wallet_dir"]
                tns_alias = conexion["tns_alias"]
                user = conexion["user"]
                password = conexion["password"]

                cx_Oracle.init_oracle_client(config_dir=wallet_dir)

                connection = cx_Oracle.connect(
                    user=user,
                    password=password,
                    dsn=tns_alias,
                    encoding="UTF-8"
                )

            elif conexion.get("tipo") == "local":
                host = conexion["host"]
                port = int(conexion["port"])
                service_name = conexion["service_name"]
                user = conexion["user"]
                password = conexion["password"]

                dsn = cx_Oracle.makedsn(host, port, service_name=service_name)

                connection = cx_Oracle.connect(
                    user=user,
                    password=password,
                    dsn=dsn,
                    encoding="UTF-8"
                )
            else:
                self.resultado.insert("end", f"❌ Tipo de conexión '{conexion.get('tipo')}' no válido\n")
                return

            self.resultado.insert("end", f"✅ Conexión exitosa a {nomconexion}\n")
            self.resultado.insert("end", f"Versión del servidor: {connection.version}\n\n")
            connection.close()

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self.resultado.insert("end", f"❌ Error ORA-{error.code}: {error.message}\n\n")
        except Exception as e:
            self.resultado.insert("end", f"❌ Error inesperado: {str(e)}\n\n")

# Ejecutar app
if __name__ == "__main__":
    app = App()
    app.mainloop()

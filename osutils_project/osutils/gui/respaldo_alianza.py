import customtkinter as ctk
from tkinter import filedialog
from osutils.gui.conexion import SelectorConexionOracle
from osutils.db.oracle import OracleConnectionManager
import os
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(sys.argv[0]))

# Lista de tablas a respaldar en orden (por defecto)
TABLAS_RESPALDO_DEFAULT = [
    "ALIANZA", "ALIANZA_PLAN_PROD"
]

# Función para cargar tablas desde archivo si existe
def cargar_tablas_respaldo():
    ruta = os.path.join(get_base_path(), "Tablas_alianza.txt")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            tablas = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        if tablas:
            return tablas
    return TABLAS_RESPALDO_DEFAULT

class RespaldoAlianzaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.tablas_respaldo = cargar_tablas_respaldo()
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=10, padx=30, fill="both", expand=True)
        # Selector de conexión (sin selección inicial)
        self.selector = SelectorConexionOracle(content_frame)
        self.selector.combo.set("")
        self.selector.pack(pady=10, anchor="w")
        ctk.CTkLabel(content_frame, text="Selecciona una Alianza:").pack(pady=5, anchor="w")
        self.alianza_combo = ctk.CTkOptionMenu(content_frame, values=[], command=None, width=320)
        self.alianza_combo.set("")
        self.alianza_combo.pack(pady=5, anchor="w")
        self.btn_descargar = ctk.CTkButton(content_frame, text="Descargar Alianza", command=self.descargar_alianza)
        self.btn_descargar.pack(pady=20, anchor="w")
        self.mensaje = ctk.CTkLabel(content_frame, text="", font=("Arial", 14))
        self.mensaje.pack(pady=10, anchor="w")
        self.alianzas = []
        # Asignar el evento de selección solo después de crear el combo
        self.selector.combo.configure(command=self.on_conexion_selected)
    def on_conexion_selected(self, value):
        self.mensaje.configure(text="Cargando alianzas...")
        self.alianza_combo.set("")
        self.alianza_combo.configure(values=[])
        self.alianzas = []
        try:
            connection = self.selector.connect()
            cursor = connection.cursor()
            cursor.execute("SELECT codalianza, descalianza FROM GORAPR.ALIANZA ORDER BY codalianza")
            self.alianzas = [(str(row[0]), row[1]) for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            opciones = [f"{cod} - {desc}" for cod, desc in self.alianzas]
            self.alianza_combo.configure(values=opciones)
            self.mensaje.configure(text=f"{len(self.alianzas)} alianzas encontradas.")
        except Exception as e:
            self.mensaje.configure(text=f"❌ Error al obtener alianzas: {str(e)}")
    def obtener_pk_tabla(self, cursor, tabla):
        sql = '''
            SELECT cols.column_name
            FROM all_constraints cons
            JOIN all_cons_columns cols ON cons.constraint_name = cols.constraint_name AND cons.owner = cols.owner
            WHERE cons.constraint_type = 'P'
              AND cons.owner = 'GORAPR'
              AND cons.table_name = :tabla
            ORDER BY cols.position
        '''
        cursor.execute(sql, [tabla])
        return [row[0] for row in cursor.fetchall()]
    def descargar_alianza(self):
        idx = self.alianza_combo.cget("values").index(self.alianza_combo.get()) if self.alianza_combo.get() else -1
        if idx == -1:
            self.mensaje.configure(text="⚠️ Selecciona una alianza primero.")
            return
        codalianza, descalianza = self.alianzas[idx]
        try:
            connection = self.selector.connect()
            cursor = connection.cursor()
            inserts = []
            deletes = []
            from datetime import datetime
            import os
            fecha_hoy = datetime.now().strftime("%d%m%Y")
            # AMBIENTACION: Encabezado de script
            inserts.append("PROMPT ------------------------------------------------------------------------------------------------")
            inserts.append(f"PROMPT --            INICIA  AMBIENTACIÓN ALIANZA  ({codalianza} - {descalianza})")
            inserts.append("PROMPT ------------------------------------------------------------------------------------------------\n")
            # REVERSO: Encabezado de script
            deletes.append("PROMPT ------------------------------------------------------------------------------------------------")
            deletes.append(f"PROMPT --            INICIA  REVERSO ALIANZA  ({codalianza} - {descalianza})")
            deletes.append("PROMPT ------------------------------------------------------------------------------------------------\n")
            # AMBIENTACION: inserts en orden, REVERSO: deletes en orden inverso
            tablas_orden = self.tablas_respaldo 
            tablas_reverso = list(self.tablas_respaldo)[::-1]
            # AMBIENTACION
            for tabla in tablas_orden:
                inserts.append("PROMPT ------------------------------------------------------------------------------------------------")
                inserts.append(f"PROMPT -- INSERTANDO TABLA [{tabla}]  ALIANZA ({codalianza})")
                inserts.append("PROMPT ------------------------------------------------------------------------------------------------\n")
                pk_cols = self.obtener_pk_tabla(cursor, tabla)
                order_by = f" ORDER BY {', '.join(pk_cols)}" if pk_cols else ""
                cursor.execute(f"SELECT * FROM GORAPR.{tabla} WHERE codalianza=:1{order_by}", [codalianza])
                # Ajuste para palabras reservadas en columnas
                def quote_column(col):
                    reserved = {'DEFAULT', 'SELECT', 'FROM', 'WHERE', 'ORDER', 'GROUP', 'TABLE', 'INSERT', 'UPDATE', 'DELETE'}
                    return f'"{col}"' if col.upper() in reserved else col
                columns = [quote_column(col[0]) for col in cursor.description]
                rows = cursor.fetchall()
                for row in rows:
                    values = []
                    for v in row:
                        if v is None:
                            values.append("NULL")
                        elif isinstance(v, str):
                            values.append("'" + v.replace("'", "''") + "'")
                        elif hasattr(v, 'strftime'):
                            values.append(f"TO_DATE('{v.strftime('%d/%m/%Y')}', 'DD/MM/YYYY')")
                        else:
                            values.append(str(v))
                    insert_sql = f"INSERT INTO {tabla}\n       (" + ",".join(columns) + ")\nVALUES (" + ",".join(values) + ")\n/\n"
                    inserts.append(insert_sql)
                inserts.append("PROMPT ------------------------------------------------------------------------------------------------")
                inserts.append(f"PROMPT -- FINALIZÓ INSERTS TABLA [{tabla}]  ALIANZA ({codalianza})")
                inserts.append("PROMPT ------------------------------------------------------------------------------------------------\n")
            inserts.append("PROMPT ------------------------------------------------------------------------------------------------")
            inserts.append(f"PROMPT --            FINALIZÓ  AMBIENTACIÓN ALIANZA ({codalianza} - {descalianza})")
            inserts.append("PROMPT ------------------------------------------------------------------------------------------------\n")
            # REVERSO
            for tabla in tablas_reverso:
                deletes.append("PROMPT ------------------------------------------------------------------------------------------------")
                deletes.append(f"PROMPT -- ELIMINANDO TABLA [{tabla}]  ALIANZA ({codalianza})")
                deletes.append("PROMPT ------------------------------------------------------------------------------------------------\n")
                delete_sql = f"DELETE FROM {tabla} WHERE CODALIANZA = '{codalianza}';\n/\n"
                deletes.append(delete_sql)
            deletes.append("PROMPT ------------------------------------------------------------------------------------------------")
            deletes.append(f"PROMPT --            FINALIZÓ  REVERSO ALIANZA ({codalianza} - {descalianza})")
            deletes.append("PROMPT ------------------------------------------------------------------------------------------------\n")
            cursor.close()
            connection.close()
            # Pedir solo la carpeta
            carpeta = filedialog.askdirectory(title="Selecciona la carpeta de guardado")
            if carpeta:
                nombre_ambi = f"AMBIENTACION_ALIANZA_{codalianza}_{fecha_hoy}.sql"
                nombre_rev = f"REVERSO_ALIANZA_{codalianza}_{fecha_hoy}.sql"
                ruta_ambi = os.path.join(carpeta, nombre_ambi)
                ruta_rev = os.path.join(carpeta, nombre_rev)
                with open(ruta_ambi, "w", encoding="ansi") as f:
                    f.write("\n".join(inserts))
                with open(ruta_rev, "w", encoding="ansi") as f:
                    f.write("\n".join(deletes))
                self.mensaje.configure(text=f"✅ Archivos guardados:\n{ruta_ambi}\n{ruta_rev}")
            else:
                self.mensaje.configure(text="Operación cancelada.")
        except Exception as e:
            self.mensaje.configure(text=f"❌ Error al respaldar alianza: {str(e)}")

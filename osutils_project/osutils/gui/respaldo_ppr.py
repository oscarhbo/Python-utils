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

# Lista de tablas a respaldar para PPR (modifica según tus necesidades)
TABLAS_RESPALDO_PPR = [
    "PLAN_PROD","TABLA_PPR2"
]

def cargar_tablas_respaldo_ppr():
    ruta = os.path.join(get_base_path(), "Tablas_ppr.txt")
    tablas = []
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                partes = line.split("|")
                tabla = partes[0]
                params = {}
                for p in partes[1:]:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        params[k.strip().upper()] = v.strip()
                # CODLVAL_FMT puede tener = o no, así que lo tratamos aparte
                for p in partes[1:]:
                    if p.startswith("CODLVAL_FMT="):
                        params["CODLVAL_FMT"] = p[len("CODLVAL_FMT="):]
                tablas.append({"tabla": tabla, "params": params})
    if not tablas:
        # fallback clásico
        return [{"tabla": t, "params": {}} for t in TABLAS_RESPALDO_PPR]
    return tablas

class RespaldoPPRFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.tablas_respaldo = cargar_tablas_respaldo_ppr()
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=10, padx=30, fill="both", expand=True)
        # Selector de conexión ORIGEN
        self.selector = SelectorConexionOracle(content_frame)
        self.selector.combo.set("")
        self.selector.pack(pady=10, anchor="w")
        # Selector de conexión DESTINO opcional
        ctk.CTkLabel(content_frame, text="Selecciona conexión destino (opcional):").pack(pady=5, anchor="w")
        self.selector_destino = SelectorConexionOracle(content_frame)
        self.selector_destino.combo.set("")
        self.selector_destino.pack(pady=10, anchor="w")
        ctk.CTkLabel(content_frame, text="Ingresa el PPR a descargar (CODPROD-CODPLAN-REVPLAN):").pack(pady=5, anchor="w")
        self.ppr_entry = ctk.CTkEntry(content_frame, width=320)
        self.ppr_entry.pack(pady=5, anchor="w")
        self.btn_descargar = ctk.CTkButton(content_frame, text="Descargar PPR", command=self.descargar_ppr)
        self.btn_descargar.pack(pady=20, anchor="w")
        self.mensaje = ctk.CTkLabel(content_frame, text="", font=("Arial", 14))
        self.mensaje.pack(pady=10, anchor="w")
        # ...similar a respaldo_alianza, pero usando CODPROD, CODPLAN, REVPLAN...

    def obtener_columnas_destino(self, tabla):
        conexion_nombre_dest = self.selector_destino.get_selected()
        if not conexion_nombre_dest:
            return None
        try:
            config = self.selector_destino.config
            connection = OracleConnectionManager.connect(config, conexion_nombre_dest)
            cursor = connection.cursor()
            cursor.execute("SELECT column_name FROM all_tab_columns WHERE owner = 'GORAPR' AND table_name = :1 ORDER BY column_id", [tabla])
            columnas = [row[0] for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            if not columnas:
                raise Exception(f"❌ La tabla '{tabla}' no existe en la conexión destino.")
            return columnas
        except Exception as e:
            raise e

    def descargar_ppr(self):
        self.btn_descargar.configure(state="disabled")
        self.mensaje.update()
        self.master.configure(cursor="wait")
        self.update()
        try:
            ppr = self.ppr_entry.get().strip()
            if not ppr or '-' not in ppr:
                self.mensaje.configure(text="⚠️ Ingresa el PPR en formato CODPROD-CODPLAN-REVPLAN.")
                return
            try:
                codprod, codplan, revplan = ppr.split('-', 2)
            except Exception:
                self.mensaje.configure(text="⚠️ Formato de PPR incorrecto. Usa CODPROD-CODPLAN-REVPLAN.")
                return
            connection = self.selector.connect()
            cursor = connection.cursor()
            inserts = []
            deletes = []
            from datetime import datetime
            fecha_hoy = datetime.now().strftime("%d%m%Y")
            tablas_orden = self.tablas_respaldo
            tablas_reverso = list(self.tablas_respaldo)[::-1]

            inserts.append("--                               (Control Encoding- ñÑáÁéÉíÍóÓúÚ)                                     \n")  
            inserts.append("PROMPT |------------------------------------------------------------------------------------------------|")
            inserts.append(f"PROMPT |                  INICIA  AMBIENTACIÓN PPR ({ppr})             ")      
            inserts.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
            
            for tabla_info in tablas_orden:
                tabla = tabla_info["tabla"] if isinstance(tabla_info, dict) else tabla_info
                params = tabla_info["params"] if isinstance(tabla_info, dict) else {}
                inserts.append("PROMPT |------------------------------------------------------------------------------------------------|")
                inserts.append(f"PROMPT |                     INSERTANDO TABLA [{tabla}]  PPR ({ppr})")
                inserts.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                # Obtener columnas PK para ORDER BY
                cursor.execute("""
                    SELECT cols.column_name
                    FROM all_constraints cons, all_cons_columns cols
                    WHERE cons.constraint_type = 'P'
                      AND cons.owner = 'GORAPR'
                      AND cons.table_name = :1
                      AND cons.constraint_name = cols.constraint_name
                      AND cons.owner = cols.owner
                    ORDER BY cols.position
                """, [tabla])
                pk_cols = [row[0] for row in cursor.fetchall()]
                order_by = f" ORDER BY {', '.join(pk_cols)}" if pk_cols else ""
                # --- Lógica especial para LVAL ---
                if tabla == "LVAL" and ("TIPOLVAL" in params or "CODLVAL_FMT" in params):
                    tipolval = params.get("TIPOLVAL", "CRITRESE")
                    codlval_fmt = params.get("CODLVAL_FMT", "{CODPROD}{CODPLAN}{REVPLAN}")
                    codlval = codlval_fmt.replace("{CODPROD}", codprod).replace("{CODPLAN}", codplan).replace("{REVPLAN}", revplan)
                    cursor.execute(f"SELECT * FROM GORAPR.LVAL WHERE TIPOLVAL=:1 AND CODLVAL=:2{order_by}", [tipolval, codlval])
                else:
                    cursor.execute(f"SELECT * FROM GORAPR.{tabla} WHERE CODPROD=:1 AND CODPLAN=:2 AND REVPLAN=:3{order_by}", [codprod, codplan, revplan])
                def quote_column(col):
                    reserved = {'DEFAULT', 'SELECT', 'FROM', 'WHERE', 'ORDER', 'GROUP', 'TABLE', 'INSERT', 'UPDATE', 'DELETE'}
                    return f'"{col}"' if col.upper() in reserved else col
                try:
                    columnas_destino = self.obtener_columnas_destino(tabla)
                except Exception as e:
                    self.mensaje.configure(text=str(e))
                    cursor.close()
                    connection.close()
                    return
                columns_all = [col[0] for col in cursor.description]
                if columnas_destino:
                    columnas_filtradas = [c for c in columns_all if c in columnas_destino]
                else:
                    columnas_filtradas = columns_all
                columns = [quote_column(col) for col in columnas_filtradas]
                rows = cursor.fetchall()
                idxs = [columns_all.index(c) for c in columnas_filtradas]
                for row in rows:
                    values = []
                    for idx_col, i in enumerate(idxs):
                        col_name = columnas_filtradas[idx_col]
                        v = row[i]
                        if tabla == "CONF_CRITERIO_CTA" and col_name == "IDCRICTA":
                            values.append("SQ_CONF_CRITERIO_CTA.NEXTVAL")
                        elif tabla == "CONFIG_LIMITE_RESP" and col_name == "IDELIMRESP":
                            values.append("(SELECT MAX(IDELIMRESP)+1 FROM CONFIG_LIMITE_RESP)")
                        elif v is None:
                            values.append("NULL")
                        elif isinstance(v, str):
                            values.append("'" + v.replace("'", "''") + "'")
                        elif hasattr(v, 'strftime'):
                            values.append(f"TO_DATE('{v.strftime('%d/%m/%Y')}', 'DD/MM/YYYY')")
                        else:
                            values.append(str(v))
                    insert_sql = f"INSERT INTO {tabla}\n       (" + ",".join(columns) + ")\nVALUES (" + ",".join(values) + ")\n/\n"
                    inserts.append(insert_sql)
                # Al final de cada tabla
                inserts.append("PROMPT |------------------------------------------------------------------------------------------------|")
                inserts.append(f"PROMPT |                     FINALIZÓ INSERTS TABLA [{tabla}]  PPR ({ppr})")
                inserts.append("PROMPT |------------------------------------------------------------------------------------------------|\n")

            inserts.append("PROMPT |------------------------------------------------------------------------------------------------|")
            inserts.append(f"PROMPT |                  FINALIZÓ  AMBIENTACIÓN PPR ({ppr})")
            inserts.append("PROMPT |------------------------------------------------------------------------------------------------|\n")


            # REVERSO
            deletes.append("--                               (Control Encoding- ñÑáÁéÉíÍóÓúÚ)                                     \n")
            deletes.append("PROMPT |------------------------------------------------------------------------------------------------|")
            deletes.append(f"PROMPT |                     INICIA  REVERSO PPR ({ppr})             ")
            deletes.append("PROMPT |------------------------------------------------------------------------------------------------|\n")

            for tabla_info in tablas_reverso:
                tabla = tabla_info["tabla"] if isinstance(tabla_info, dict) else tabla_info
                params = tabla_info["params"] if isinstance(tabla_info, dict) else {}
                deletes.append("PROMPT |------------------------------------------------------------------------------------------------|")
                deletes.append(f"PROMPT |                     ELIMINANDO TABLA [{tabla}]  PPR ({ppr})")
                deletes.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                if tabla == "LVAL" and ("TIPOLVAL" in params or "CODLVAL_FMT" in params):
                    tipolval = params.get("TIPOLVAL", "CRITRESE")
                    codlval_fmt = params.get("CODLVAL_FMT", "{CODPROD}{CODPLAN}{REVPLAN}")
                    codlval = codlval_fmt.replace("{CODPROD}", codprod).replace("{CODPLAN}", codplan).replace("{REVPLAN}", revplan)
                    delete_sql = f"DELETE FROM LVAL WHERE TIPOLVAL = '{tipolval}' AND CODLVAL = '{codlval}'\n/\n"
                else:
                    delete_sql = f"DELETE FROM {tabla} WHERE CODPROD = '{codprod}' AND CODPLAN = '{codplan}' AND REVPLAN = '{revplan}'\n/\n"
                deletes.append(delete_sql)
            deletes.append("PROMPT |------------------------------------------------------------------------------------------------|")
            deletes.append(f"PROMPT |                     FINALIZÓ  REVERSO PPR ({ppr})")
            deletes.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
            # VALIDACIÓN
            validaciones = []
            idident = 1
            for tabla_info in tablas_orden:
                tabla = tabla_info["tabla"] if isinstance(tabla_info, dict) else tabla_info
                params = tabla_info["params"] if isinstance(tabla_info, dict) else {}
                rows_count = 0
                for ins in inserts:
                    if ins.startswith(f"INSERT INTO {tabla}\n"):
                        rows_count += 1
                if rows_count == 0:
                    continue
                descripcion = f"VALIDACION {tabla} PPR {ppr}"
                if tabla == "LVAL" and ("TIPOLVAL" in params or "CODLVAL_FMT" in params):
                    tipolval = params.get("TIPOLVAL", "CRITRESE")
                    codlval_fmt = params.get("CODLVAL_FMT", "{CODPROD}{CODPLAN}{REVPLAN}")
                    codlval = codlval_fmt.replace("{CODPROD}", codprod).replace("{CODPLAN}", codplan).replace("{REVPLAN}", revplan)
                    where = f"TIPOLVAL = '{tipolval}' AND CODLVAL = '{codlval}'"
                else:
                    where = f"CODPROD = '{codprod}' AND CODPLAN = '{codplan}' AND REVPLAN = '{revplan}'"
                validaciones.append(f"  SELECT {idident} IDIDENT, '{descripcion}' DES_IDENTIFICADOR, {rows_count} CNT_BASE, COUNT(*) CNT_PROD\n  FROM {tabla}\n  WHERE {where}")
                idident += 1
            if validaciones:
                validacion_sql = (
                    "SELECT IDIDENT, DES_IDENTIFICADOR, DECODE(CNT_BASE, CNT_PROD, '[OK] VALIDACIÓN', '[ERROR] FALLÓ LA VALIDACIÓN SE ESPERABAN '||CNT_BASE||' REGISTROS Y SE OBTUVIERON '||CNT_PROD) RESULTADO, CNT_BASE, CNT_PROD\n"
                    "FROM (\n\n" +
                    "\n\n  UNION\n\n".join(validaciones) +
                    "\n\n)\nORDER BY 1\n/\n"
                )
            else:
                validacion_sql = '-- No se generaron validaciones porque no hubo inserts.'
            carpeta = filedialog.askdirectory(title="Selecciona la carpeta de guardado")
            if carpeta:
                nombre_ambi = f"AMBIENTACION_PPR_{ppr}_{fecha_hoy}.sql"
                nombre_rev = f"REVERSO_PPR_{ppr}_{fecha_hoy}.sql"
                nombre_val = f"SCRIPT_VALIDACION_PPR_{ppr}_{fecha_hoy}.sql"
                ruta_ambi = os.path.join(carpeta, nombre_ambi)
                ruta_rev = os.path.join(carpeta, nombre_rev)
                ruta_val = os.path.join(carpeta, nombre_val)
                with open(ruta_ambi, "w", encoding="ansi") as f:
                    f.write("\n".join(inserts))
                with open(ruta_rev, "w", encoding="ansi") as f:
                    f.write("\n".join(deletes))
                with open(ruta_val, "w", encoding="ansi") as f:
                    f.write(validacion_sql)
                # --- Descarga adicional para tablas de Tablas_ppr_ws.txt ---
                ruta_ws = os.path.join(get_base_path(), "Tablas_ppr_ws.txt")
                tablas_ws = []
                if os.path.exists(ruta_ws):
                    with open(ruta_ws, "r", encoding="utf-8") as f:
                        tablas_ws = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
                if tablas_ws:
                    inserts_ws = []
                    deletes_ws = []
                    validaciones_ws = []
                    idident_ws = 1
                    inserts_ws.append("--                               (Control Encoding- ñÑáÁéÉíÍóÓúÚ)                                     \n")
                    inserts_ws.append("PROMPT |------------------------------------------------------------------------------------------------|")
                    inserts_ws.append(f"PROMPT |                  INICIA  AMBIENTACIÓN WS_{ppr}             ")
                    inserts_ws.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                    for tabla_info in tablas_ws:
                        tabla = tabla_info["tabla"] if isinstance(tabla_info, dict) else tabla_info
                        params = tabla_info["params"] if isinstance(tabla_info, dict) else {}
                        inserts_ws.append("PROMPT |------------------------------------------------------------------------------------------------|")
                        inserts_ws.append(f"PROMPT |                     INSERTANDO TABLA [{tabla}]  WS_{ppr}")
                        inserts_ws.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                        # Obtener columnas PK para ORDER BY
                        cursor.execute("""
                            SELECT cols.column_name
                            FROM all_constraints cons, all_cons_columns cols
                            WHERE cons.constraint_type = 'P'
                              AND cons.owner = 'GORAPR'
                              AND cons.table_name = :1
                              AND cons.constraint_name = cols.constraint_name
                              AND cons.owner = cols.owner
                            ORDER BY cols.position
                        """, [tabla])
                        pk_cols = [row[0] for row in cursor.fetchall()]
                        order_by = f" ORDER BY {', '.join(pk_cols)}" if pk_cols else ""
                        if tabla == "LVAL" and ("TIPOLVAL" in params or "CODLVAL_FMT" in params):
                            tipolval = params.get("TIPOLVAL", "CRITRESE")
                            codlval_fmt = params.get("CODLVAL_FMT", "{CODPROD}{CODPLAN}{REVPLAN}")
                            codlval = codlval_fmt.replace("{CODPROD}", codprod).replace("{CODPLAN}", codplan).replace("{REVPLAN}", revplan)
                            cursor.execute(f"SELECT * FROM GORAPR.LVAL WHERE TIPOLVAL=:1 AND CODLVAL=:2{order_by}", [tipolval, codlval])
                        else:
                            cursor.execute(f"SELECT * FROM GORAPR.{tabla} WHERE CODPROD=:1 AND CODPLAN=:2 AND REVPLAN=:3{order_by}", [codprod, codplan, revplan])
                        def quote_column(col):
                            reserved = {'DEFAULT', 'SELECT', 'FROM', 'WHERE', 'ORDER', 'GROUP', 'TABLE', 'INSERT', 'UPDATE', 'DELETE'}
                            return f'"{col}"' if col.upper() in reserved else col
                        try:
                            columnas_destino = self.obtener_columnas_destino(tabla)
                        except Exception as e:
                            self.mensaje.configure(text=str(e))
                            cursor.close()
                            connection.close()
                            return
                        columns_all = [col[0] for col in cursor.description]
                        if columnas_destino:
                            columnas_filtradas = [c for c in columns_all if c in columnas_destino]
                        else:
                            columnas_filtradas = columns_all
                        columns = [quote_column(col) for col in columnas_filtradas]
                        rows = cursor.fetchall()
                        idxs = [columns_all.index(c) for c in columnas_filtradas]
                        for row in rows:
                            values = []
                            for idx_col, i in enumerate(idxs):
                                col_name = columnas_filtradas[idx_col]
                                v = row[i]
                                if tabla == "CONF_CRITERIO_CTA" and col_name == "IDCRICTA":
                                    values.append("SQ_CONF_CRITERIO_CTA.NEXTVAL")
                                elif tabla == "CONFIG_LIMITE_RESP" and col_name == "IDELIMRESP":
                                    values.append("(SELECT MAX(IDELIMRESP)+1 FROM CONFIG_LIMITE_RESP)")
                                elif v is None:
                                    values.append("NULL")
                                elif isinstance(v, str):
                                    values.append("'" + v.replace("'", "''") + "'")
                                elif hasattr(v, 'strftime'):
                                    values.append(f"TO_DATE('{v.strftime('%d/%m/%Y')}', 'DD/MM/YYYY')")
                                else:
                                    values.append(str(v))
                            insert_sql = f"INSERT INTO {tabla}\n       (" + ",".join(columns) + ")\nVALUES (" + ",".join(values) + ")\n/\n"
                            inserts_ws.append(insert_sql)
                        inserts_ws.append("PROMPT |------------------------------------------------------------------------------------------------|")
                        inserts_ws.append(f"PROMPT |                     FINALIZÓ INSERTS TABLA [{tabla}]  WS_{ppr}")
                        inserts_ws.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                    inserts_ws.append("PROMPT |------------------------------------------------------------------------------------------------|")
                    inserts_ws.append(f"PROMPT |                  FINALIZÓ  AMBIENTACIÓN WS_{ppr}")
                    inserts_ws.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                    # REVERSO WS
                    deletes_ws.append("--                               (Control Encoding- ñÑáÁéÉíÍóÓúÚ)                                     \n")
                    deletes_ws.append("PROMPT |------------------------------------------------------------------------------------------------|")
                    deletes_ws.append(f"PROMPT |                     INICIA  REVERSO WS_{ppr}             ")
                    deletes_ws.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                    for tabla_info in tablas_ws[::-1]:
                        tabla = tabla_info["tabla"] if isinstance(tabla_info, dict) else tabla_info
                        params = tabla_info["params"] if isinstance(tabla_info, dict) else {}
                        deletes_ws.append("PROMPT |------------------------------------------------------------------------------------------------|")
                        deletes_ws.append(f"PROMPT |                     ELIMINANDO TABLA [{tabla}]  WS_{ppr}")
                        deletes_ws.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                        if tabla == "LVAL" and ("TIPOLVAL" in params or "CODLVAL_FMT" in params):
                            tipolval = params.get("TIPOLVAL", "CRITRESE")
                            codlval_fmt = params.get("CODLVAL_FMT", "{CODPROD}{CODPLAN}{REVPLAN}")
                            codlval = codlval_fmt.replace("{CODPROD}", codprod).replace("{CODPLAN}", codplan).replace("{REVPLAN}", revplan)
                            delete_sql = f"DELETE FROM LVAL WHERE TIPOLVAL = '{tipolval}' AND CODLVAL = '{codlval}'\n/\n"
                        else:
                            delete_sql = f"DELETE FROM {tabla} WHERE CODPROD = '{codprod}' AND CODPLAN = '{codplan}' AND REVPLAN = '{revplan}'\n/\n"
                        deletes_ws.append(delete_sql)
                    deletes_ws.append("PROMPT |------------------------------------------------------------------------------------------------|")
                    deletes_ws.append(f"PROMPT |                     FINALIZÓ  REVERSO WS_{ppr}")
                    deletes_ws.append("PROMPT |------------------------------------------------------------------------------------------------|\n")
                    # VALIDACIÓN WS
                    for tabla in tablas_ws:
                        rows_count = 0
                        for ins in inserts_ws:
                            if ins.startswith(f"INSERT INTO {tabla}\n"):
                                rows_count += 1
                        if rows_count == 0:
                            continue
                        descripcion = f"VALIDACION {tabla} WS_{ppr}"
                        where = f"CODPROD = '{codprod}' AND CODPLAN = '{codplan}' AND REVPLAN = '{revplan}'"
                        validaciones_ws.append(f"  SELECT {idident_ws} IDIDENT, '{descripcion}' DES_IDENTIFICADOR, {rows_count} CNT_BASE, COUNT(*) CNT_PROD\n  FROM {tabla}\n  WHERE {where}")
                        idident_ws += 1
                    if validaciones_ws:
                        validacion_sql_ws = (
                            "SELECT IDIDENT, DES_IDENTIFICADOR, DECODE(CNT_BASE, CNT_PROD, '[OK] VALIDACIÓN', '[ERROR] FALLÓ LA VALIDACIÓN SE ESPERABAN '||CNT_BASE||' REGISTROS Y SE OBTUVIERON '||CNT_PROD) RESULTADO, CNT_BASE, CNT_PROD\n"
                            "FROM (\n\n" +
                            "\n\n  UNION\n\n".join(validaciones_ws) +
                            "\n\n)\nORDER BY 1\n/\n"
                        )
                    else:
                        validacion_sql_ws = '-- No se generaron validaciones porque no hubo inserts.'
                # Guardar archivos
                if carpeta:
                    with open(ruta_ambi, "w", encoding="ansi") as f:
                        f.write("\n".join(inserts))
                    with open(ruta_rev, "w", encoding="ansi") as f:
                        f.write("\n".join(deletes))
                    with open(ruta_val, "w", encoding="ansi") as f:
                        f.write(validacion_sql)
                    if tablas_ws:
                        nombre_ambi_ws = f"AMBIENTACION_WS_{ppr}_{fecha_hoy}.sql"
                        nombre_rev_ws = f"REVERSO_WS_{ppr}_{fecha_hoy}.sql"
                        nombre_val_ws = f"SCRIPT_VALIDACION_WS_{ppr}_{fecha_hoy}.sql"
                        ruta_ambi_ws = os.path.join(carpeta, nombre_ambi_ws)
                        ruta_rev_ws = os.path.join(carpeta, nombre_rev_ws)
                        ruta_val_ws = os.path.join(carpeta, nombre_val_ws)
                        with open(ruta_ambi_ws, "w", encoding="ansi") as f:
                            f.write("\n".join(inserts_ws))
                        with open(ruta_rev_ws, "w", encoding="ansi") as f:
                            f.write("\n".join(deletes_ws))
                        with open(ruta_val_ws, "w", encoding="ansi") as f:
                            f.write(validacion_sql_ws)
                        self.mensaje.configure(text=f"✅ Archivos guardados:\n{ruta_ambi}\n{ruta_rev}\n{ruta_val}\n{ruta_ambi_ws}\n{ruta_rev_ws}\n{ruta_val_ws}")
                    else:
                        self.mensaje.configure(text=f"✅ Archivos guardados:\n{ruta_ambi}\n{ruta_rev}\n{ruta_val}")
                else:
                    self.mensaje.configure(text="Operación cancelada.")
        except Exception as e:
            self.mensaje.configure(text=f"❌ Error al respaldar PPR: {str(e)}")
        finally:
            self.btn_descargar.configure(state="normal")
            self.master.configure(cursor="arrow")
            self.update()

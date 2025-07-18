import cx_Oracle
import threading
import os

class OracleConnectionManager:
    _oracle_client_initialized = False
    _oracle_client_lock = threading.Lock()
    _oracle_client_config_dir = None

    @staticmethod
    def connect(config, nomconexion):
        if nomconexion not in config:
            raise ValueError(f"Conexión '{nomconexion}' no encontrada")
        conexion = config[nomconexion]
        if conexion.get("tipo") == "cloud":
            wallet_dir = conexion["wallet_dir"]
            tns_alias = conexion["tns_alias"]
            user = conexion["user"]
            password = conexion["password"]
            with OracleConnectionManager._oracle_client_lock:
                if not OracleConnectionManager._oracle_client_initialized:
                    cx_Oracle.init_oracle_client(config_dir=wallet_dir)
                    OracleConnectionManager._oracle_client_initialized = True
                    OracleConnectionManager._oracle_client_config_dir = wallet_dir
                else:
                    # Si ya fue inicializado, pero con otro wallet_dir, advertir
                    if OracleConnectionManager._oracle_client_config_dir != wallet_dir:
                        raise RuntimeError(
                            "❌ Error: Oracle Client library ya fue inicializado con un wallet diferente. "
                            "Debes reiniciar la aplicación para cambiar de wallet/cloud."
                        )
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
            with OracleConnectionManager._oracle_client_lock:
                if not OracleConnectionManager._oracle_client_initialized:
                    # Inicializa el cliente sin wallet (para local)
                    cx_Oracle.init_oracle_client()
                    OracleConnectionManager._oracle_client_initialized = True
                    OracleConnectionManager._oracle_client_config_dir = None
            connection = cx_Oracle.connect(
                user=user,
                password=password,
                dsn=dsn,
                encoding="UTF-8"
            )
        else:
            raise ValueError(f"Tipo de conexión '{conexion.get('tipo')}' no válido")
        return connection

def obtener_paquete_oracle(nombre_paquete, connection):
    cursor = connection.cursor()
    query = """
        SELECT text
        FROM   all_source
        WHERE  name = :nombre
        AND    type IN ('PACKAGE', 'PACKAGE BODY')
        AND    OWNER = 'GORAPR'
        ORDER BY type, line
    """
    cursor.execute(query, {"nombre": nombre_paquete})
    lineas = cursor.fetchall()
    if not lineas:
        raise ValueError("El paquete no existe o no tienes permisos.")
    codigo = "".join([linea[0] for linea in lineas])
    cursor.close()
    return codigo

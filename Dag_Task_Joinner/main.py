import os
import yaml
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
from datetime import datetime
import logging

class YAMLToSQLProcessor:
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Configura el sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('yaml_processor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def substitute_placeholders(self, sql, properties):
        """
        Reemplaza placeholders ${VAR} por valores del properties.yaml
        Maneja variables parciales como $target_table_sales_od_order -> target_table + sufijo
        """
        if not sql:
            return sql
            
        # Primero procesar placeholders con llaves ${VAR}
        placeholders = re.findall(r'\$\{([^}]+)\}', sql)
        missing_keys = []
        
        for placeholder in placeholders:
            if placeholder in properties:
                value = str(properties[placeholder])
                sql = sql.replace(f"${{{placeholder}}}", value)
                self.logger.info(f"Placeholder ${{{placeholder}}} reemplazado por: {value}")
            else:
                missing_keys.append(placeholder)
        
        # Procesar variables simples $variable con manejo inteligente de prefijos
        # Ordenar las propiedades por longitud descendente para evitar sustituciones parciales incorrectas
        sorted_properties = sorted(properties.items(), key=lambda x: len(x[0]), reverse=True)
        
        for prop_key, prop_value in sorted_properties:
            # Buscar patrones donde la variable aparece al inicio seguida de más caracteres o fin de línea
            pattern_str = r'\$' + re.escape(prop_key) + r'(?=[_a-zA-Z0-9]|\s|$|[^a-zA-Z0-9_])'
            pattern = re.compile(pattern_str)
            
            # Encontrar todas las coincidencias y reemplazarlas de derecha a izquierda
            # para evitar problemas con los índices
            matches = list(pattern.finditer(sql))
            for match in reversed(matches):
                old_var = f"${prop_key}"
                new_value = str(prop_value)
                
                # Reemplazar específicamente esta ocurrencia
                start_pos = match.start()
                end_pos = start_pos + len(old_var)
                
                sql = sql[:start_pos] + new_value + sql[end_pos:]
                self.logger.info(f"Variable ${prop_key} reemplazada por: {new_value}")
        
        # Verificar si quedan variables sin reemplazar
        remaining_vars = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', sql)
        unresolved_vars = []
        
        for var in remaining_vars:
            # Verificar si esta variable o algún prefijo existe en properties
            found_match = False
            for prop_key in properties.keys():
                if var.startswith(prop_key):
                    found_match = True
                    break
            
            if not found_match and var not in unresolved_vars:
                unresolved_vars.append(var)
        
        if unresolved_vars:
            self.logger.warning(f"Variables sin resolver: {unresolved_vars}")
            # Solo mostrar advertencia si hay muchas variables sin resolver
            if len(unresolved_vars) > 3:
                messagebox.showwarning("Advertencia", 
                    f"Hay {len(unresolved_vars)} variables sin resolver. Ver log para detalles.")
        
        if missing_keys:
            self.logger.warning(f"Placeholders no encontrados: {missing_keys}")
            messagebox.showwarning("Advertencia", 
                f"Los siguientes placeholders no tienen valores definidos:\n{', '.join(missing_keys)}")
        
        return sql

    def validate_files(self, folder_path):
        """Valida que existan los archivos necesarios"""
        files = {
            'config': None,
            'properties': None
        }
        
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"La carpeta {folder_path} no existe")
        
        for file in os.listdir(folder_path):
            if file.endswith("_config.yaml"):
                files['config'] = os.path.join(folder_path, file)
            elif file.endswith("_properties.yaml"):
                files['properties'] = os.path.join(folder_path, file)
        
        missing = [k for k, v in files.items() if v is None]
        if missing:
            raise FileNotFoundError(f"Archivos faltantes: {', '.join([f'{m}_*.yaml' for m in missing])}")
        
        return files

    def load_yaml_file(self, file_path):
        """Carga un archivo YAML con manejo de errores"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                self.logger.info(f"Archivo cargado exitosamente: {file_path}")
                return content
        except yaml.YAMLError as e:
            raise ValueError(f"Error al parsear YAML en {file_path}: {e}")
        except UnicodeDecodeError:
            # Intentar con diferentes encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = yaml.safe_load(f)
                        self.logger.warning(f"Archivo cargado con encoding {encoding}: {file_path}")
                        return content
                except:
                    continue
            raise UnicodeDecodeError(f"No se pudo decodificar el archivo: {file_path}")

    def load_task_yaml_file(self, folder_path, filename):
        """Carga un archivo YAML de una tarea específica"""
        file_path = os.path.join(folder_path, filename)
        if not os.path.exists(file_path):
            self.logger.warning(f"Archivo de tarea no encontrado: {file_path}")
            return None
        return self.load_yaml_file(file_path)

    def extract_sql_from_task_file(self, task_content):
        """Extrae el código SQL de un archivo de tarea"""
        if not task_content:
            return ""
        
        # Buscar en diferentes ubicaciones posibles
        sql_paths = [
            ["config", "hql"],
            ["config", "sql"], 
            ["config", "query"],
            ["hql"],
            ["sql"],
            ["query"],
            ["script"],
            ["queries"]
        ]
        
        for path in sql_paths:
            temp_content = task_content
            try:
                for key in path:
                    temp_content = temp_content[key]
                if temp_content and isinstance(temp_content, str):
                    return temp_content
            except (KeyError, TypeError):
                continue
        
        self.logger.warning("No se encontró código SQL en el archivo de tarea")
        return ""

    def process_task(self, task, folder_path, properties_content):
        """Procesa una tarea individual según su tipo"""
        task_name = task.get('name', 'unknown')
        task_type = task.get('type', 'unknown')
        
        result = f"-- Tarea: {task_name}\n"
        
        if task_type == "START":
            result += f"-- Tipo: START\n"
            result += f"-- {task_name}\n\n"
            
        elif task_type == "END":
            result += f"-- Tipo: END\n"
            result += f"-- {task_name}\n"
            
            # Agregar información adicional si existe
            properties = task.get('properties', {})
            if properties:
                result += f"-- Propiedades:\n"
                for key, value in properties.items():
                    result += f"--   {key}: {value}\n"
            result += "\n"
            
        elif task_type == "SCRIPT":
            script_file = task.get('properties', {}).get('script_file', '')
            result += f"-- Tipo: SCRIPT\n"
            result += f"-- {task_name} {script_file}\n\n"
            
        elif task_type in ["SPARK_SQL", "HIVE"]:
            properties_file = task.get('properties_file', '')
            result += f"-- Tipo: {task_type}\n"
            result += f"-- {task_name} {properties_file}\n"
            
            if properties_file:
                # Cargar el archivo de propiedades de la tarea
                task_content = self.load_task_yaml_file(folder_path, properties_file)
                
                if task_content:
                    # Extraer SQL del archivo de tarea
                    sql_code = self.extract_sql_from_task_file(task_content)
                    
                    if sql_code:
                        # Sustituir placeholders en el SQL
                        sql_processed = self.substitute_placeholders(sql_code, properties_content)
                        result += f"\n{sql_processed}\n\n"
                    else:
                        result += f"-- ADVERTENCIA: No se encontró código SQL en {properties_file}\n\n"
                else:
                    result += f"-- ERROR: No se pudo cargar el archivo {properties_file}\n\n"
            else:
                result += f"-- ADVERTENCIA: No se especificó archivo de propiedades para la tarea\n\n"
        else:
            result += f"-- Tipo: {task_type} (tipo desconocido)\n"
            result += f"-- {task_name}\n\n"
        
        return result

    def process_all_tasks(self, config_content, folder_path, properties_content):
        """Procesa todas las tareas del archivo config en orden"""
        tasks = config_content.get('tasks', [])
        
        if not tasks:
            raise ValueError("No se encontraron tareas en el archivo config")
        
        consolidated_sql = ""
        
        self.logger.info(f"Procesando {len(tasks)} tareas...")
        
        for i, task in enumerate(tasks, 1):
            task_name = task.get('name', f'tarea_{i}')
            self.logger.info(f"Procesando tarea {i}/{len(tasks)}: {task_name}")
            
            task_sql = self.process_task(task, folder_path, properties_content)
            consolidated_sql += task_sql
            
            # Agregar separador entre tareas (excepto la última)
            if i < len(tasks):
                consolidated_sql += f"-- {'='*60}\n\n"
        
        return consolidated_sql

    def generate_header(self, config_file, properties_content):
        """Genera la cabecera del archivo SQL consolidado"""
        config_name = os.path.basename(config_file).replace(".yaml", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""-- ===============================================
-- ARCHIVO SQL CONSOLIDADO - TODAS LAS TAREAS
-- ===============================================
-- Configuración: {config_name}
-- Generado: {timestamp}
-- ===============================================

"""
        
        # Agregar información de propiedades si existe
        if properties_content:
            header += "-- PROPIEDADES UTILIZADAS:\n"
            for key, value in properties_content.items():
                header += f"-- {key}: {value}\n"
            header += f"-- {'='*50}\n\n"
        
        return header

    def process_files(self, folder_path):
        """Procesa los archivos YAML y genera el SQL consolidado"""
        try:
            self.logger.info(f"Iniciando procesamiento en: {folder_path}")
            
            # Validar y obtener archivos principales
            files = self.validate_files(folder_path)
            
            # Cargar contenido de archivos principales
            config_content = self.load_yaml_file(files['config'])
            properties_content = self.load_yaml_file(files['properties'])
            
            # Procesar todas las tareas
            consolidated_sql = self.process_all_tasks(config_content, folder_path, properties_content)
            
            # Agregar cabecera
            header = self.generate_header(files['config'], properties_content)
            final_sql = header + consolidated_sql
            
            # Guardar archivo final
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config_name = os.path.basename(files['config']).replace("_config.yaml", "")
            output_file = os.path.join(folder_path, f"consolidated_{config_name}_{timestamp}.sql")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_sql)
            
            # Contar tareas procesadas
            num_tasks = len(config_content.get('tasks', []))
            
            self.logger.info(f"SQL consolidado generado exitosamente en: {output_file}")
            messagebox.showinfo("Éxito", 
                f"SQL consolidado generado exitosamente en:\n{output_file}\n\n"
                f"Tareas procesadas: {num_tasks}\n"
                f"Líneas generadas: {len(final_sql.splitlines())}")
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error durante el procesamiento: {e}")
            messagebox.showerror("Error", f"Ocurrió un error durante el procesamiento:\n{e}")
            return None

    def create_gui(self):
        """Crea una interfaz gráfica mejorada"""
        root = tk.Tk()
        root.title("Procesador YAML a SQL - Consolidador de Tareas")
        root.geometry("600x350")
        root.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Procesador YAML a SQL", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Subtítulo
        subtitle_label = ttk.Label(main_frame, text="Consolidador de Tareas", 
                                  font=("Arial", 12, "italic"))
        subtitle_label.pack(pady=(0, 20))
        
        # Descripción
        desc_label = ttk.Label(main_frame, 
            text="Selecciona una carpeta que contenga:\n"
                 "• *_config.yaml (con las tareas definidas)\n"
                 "• *_properties.yaml (con las variables)\n"
                 "• Archivos .yaml de cada tarea SPARK_SQL/HIVE\n\n"
                 "El programa procesará todas las tareas en orden y generará\n"
                 "un archivo SQL consolidado con todo el código.",
            font=("Arial", 10), justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Botón para seleccionar carpeta
        select_btn = ttk.Button(button_frame, text="Seleccionar Carpeta", 
                               command=lambda: self.select_folder_and_process(),
                               width=20)
        select_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para salir
        exit_btn = ttk.Button(button_frame, text="Salir", 
                             command=root.destroy,
                             width=10)
        exit_btn.pack(side=tk.RIGHT)
        
        # Barra de estado
        self.progress_var = tk.StringVar(value="Listo para procesar...")
        self.status_label = ttk.Label(main_frame, textvariable=self.progress_var,
                                     font=("Arial", 9))
        self.status_label.pack(pady=(20, 0))
        
        self.root = root
        return root

    def select_folder_and_process(self):
        """Selecciona carpeta y procesa archivos"""
        self.progress_var.set("Seleccionando carpeta...")
        self.root.update()
        
        folder_selected = filedialog.askdirectory(title="Selecciona la carpeta con los archivos YAML")
        
        if folder_selected:
            self.progress_var.set("Procesando tareas...")
            self.root.update()
            
            result = self.process_files(folder_selected)
            
            if result:
                self.progress_var.set("¡Procesamiento completado exitosamente!")
            else:
                self.progress_var.set("Error en el procesamiento")
        else:
            self.progress_var.set("No se seleccionó ninguna carpeta")

def main():
    processor = YAMLToSQLProcessor()
    root = processor.create_gui()
    root.mainloop()

if __name__ == "__main__":
    main()
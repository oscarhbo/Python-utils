import pandas as pd
from bs4 import BeautifulSoup
import re 

def extract_data_from_html_to_excel(html_file_path, output_excel_file_path):
    """
    Extrae datos de una tabla HTML específica, manejando diferentes estructuras
    para tablas y campos, y guarda la información en un archivo Excel.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')

        target_table = None
        tables = soup.find_all('table')

        for table in tables:
            first_row = table.find('tr')
            if first_row:
                cells_in_first_row = [cell.get_text(strip=True) for cell in first_row.find_all(['td', 'th'])]
                if "Data Lake Consumption Tables and Attributes" in cells_in_first_row:
                    target_table = table
                    break

        if not target_table:
            print(f"Error: No se encontró la tabla con el encabezado 'Data Lake Consumption Tables and Attributes' en '{html_file_path}'.")
            return

        header_row_elements = target_table.find('tr')
        if not header_row_elements:
            print("Error: La tabla encontrada no tiene filas de encabezado.")
            return

        headers_found = [td.get_text(strip=True) for td in header_row_elements.find_all(['td', 'th'])]
        headers_normalized = [h.lower() for h in headers_found]
        
        column_indices = {}
        expected_columns = {
            'use case id': 'Use Case ID', 
            'use case': 'Use Case Title', 
            'data lake consumption tables and attributes': 'Data Lake Consumption Tables and Attributes'
        }

        for expected_lower_key, original_name in expected_columns.items():
            try:
                column_indices[original_name] = headers_normalized.index(expected_lower_key)
            except ValueError:
                print(f"Error: No se encontró la columna '{original_name}' en la tabla.")
                print(f"Encabezados encontrados (normalizados): {headers_normalized}")
                return

        use_case_id_col_idx = column_indices['Use Case ID']
        use_case_title_col_idx = column_indices['Use Case Title']
        data_lake_consumption_col_idx = column_indices['Data Lake Consumption Tables and Attributes']

        data_rows = []

        for row in target_table.find_all('tr')[1:]:
            cols = row.find_all('td')

            if len(cols) > max(use_case_id_col_idx, use_case_title_col_idx, data_lake_consumption_col_idx):
                use_case_id = cols[use_case_id_col_idx].get_text(strip=True)
                use_case_title = cols[use_case_title_col_idx].get_text(strip=True)
                data_lake_consumption_cell = cols[data_lake_consumption_col_idx]
                
                current_table = None
                
                elements_to_process = data_lake_consumption_cell.find_all(['p', 'li'])

                for element in elements_to_process:
                    text_content = element.get_text(separator=' ', strip=True)

                    if any(s in text_content.lower() for s in ['won\'t consider it', 'data science predictions', 'full table required', 'data science predictions']):
                        continue

                    is_table_candidate = False
                    table_name = None
                    
                    if 'mx_cust_secured_cons_dtmsh_tables.' in text_content:
                        table_name = text_content.split('mx_cust_secured_cons_dtmsh_tables.')[-1].strip()
                        is_table_candidate = True
                    elif 'Table -' in text_content:
                        table_name = text_content.split('Table -', 1)[-1].strip()
                        if table_name and element.find('strong'): 
                            table_name = element.find('strong').get_text(strip=True)
                        is_table_candidate = True
                    elif element.name == 'p' and element.find('strong') and not element.find('li'): 
                        table_name = element.find('strong').get_text(strip=True)
                        is_table_candidate = True
                    elif element.name == 'p' and text_content.strip() and not element.find('li') and not element.find('ul') and not element.find('ol'):
                        if element.find('strong'):
                            table_name = element.find('strong').get_text(strip=True)
                            is_table_candidate = True
                        elif text_content.strip() and text_content.strip() == text_content.strip().upper() and len(text_content.strip()) > 5: 
                            table_name = text_content.strip()
                            is_table_candidate = True


                    if is_table_candidate and table_name:
                        table_name = re.sub(r'[\(\)\*\:]', '', table_name).strip()
                        current_table = table_name
                    elif element.name == 'li' and current_table:
                        field_text = element.get_text(separator='\n', strip=True)
                        
                        for field_line in field_text.split('\n'):
                            field = field_line.strip()
                            if field:
                                field = re.sub(r'\s*\([^)]*\)', '', field).strip() 
                                field = re.sub(r'\s*\*$', '', field).strip() 
                                field = field.replace(':', '').strip() 
                                field = re.sub(r'^\-\s*', '', field).strip() 
                                field = re.sub(r'\s*\<br\/\>$', '', field).strip()
                                field = re.sub(r'[\u200b-\u200D\uFEFF]', '', field) 

                                if field and (re.match(r'^[A-Z0-9_]+$', field) or re.match(r'^[a-zA-Z0-9_]+$', field)):
                                    data_rows.append([use_case_id, use_case_title, current_table, field])
                            
        df = pd.DataFrame(data_rows, columns=["Caso de Uso", "Título del Caso de Uso", "Tabla", "Campo"])

        df.to_excel(output_excel_file_path, index=False, engine='openpyxl')
        print(f"La información se ha extraído y guardado exitosamente en '{output_excel_file_path}'.")
        print(f"Total de filas de datos extraídas: {len(data_rows)}")


    except FileNotFoundError:
        print(f"Error: El archivo '{html_file_path}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

rutaBase = "d:\\Repositorios\\Git\\Python-utils\\Archivos\\"
html_input_file = rutaBase + 'Casos_de_Uso.html'
excel_output_file = rutaBase + 'Casos_de_Uso_SAMS_Extraidos.xlsx'
extract_data_from_html_to_excel(html_input_file, excel_output_file)
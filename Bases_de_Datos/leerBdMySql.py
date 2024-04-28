import pymysql
import csv
import configparser

parser = configparser.ConfigParser()
parser.read("conexiones.conf")
hostname = parser.get("mysql_config", "hostname")
port = parser.get("mysql_config", "port")
username = parser.get("mysql_config", "username")
dbname = parser.get("mysql_config", "database")
password = parser.get("mysql_config", "password")

conn = pymysql.connect(host=hostname,
        user=username,
        password=password,
        db=dbname,
        port=int(port))

if conn is None:
  print("Error al conectarse a la base de datos MySQL")
else:
  print("Conexión MySQL establecida!")

  m_query = "SELECT * FROM Orders;"

local_filename = "order_extract.csv"

m_cursor = conn.cursor()
m_cursor.execute(m_query)
results = m_cursor.fetchall()

# results es una tupla con los registros
print(type(results))

print('-' * 60)
print('-- Datos Cursor')
print('-' * 60)
print(results)
print('-' * 60)

with open(local_filename, 'w', newline='') as fp:
  csv_w = csv.writer(fp, delimiter='|')
  csv_w.writerows(results)

fp.close() 
m_cursor.close()
conn.close()

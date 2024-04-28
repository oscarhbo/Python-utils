from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import configparser
import csv

parser = configparser.ConfigParser()
parser.read("conexiones.conf")
hostname = parser.get("mysql_config", "hostname")
port = parser.get("mysql_config", "port")
username = parser.get("mysql_config", "username")
dbname = parser.get("mysql_config", "database")
password = parser.get("mysql_config", "password")

database_url = f"mysql+pymysql://{username}:{password}@{hostname}:{port}/{dbname}"

engine = create_engine(database_url)

Session = sessionmaker(bind=engine)

with Session() as session:
    try:
        session.execute(text('SELECT 1'))
        print("Conexión MySQL establecida!")

        query = text("SELECT * FROM Orders;")

        result = session.execute(query).fetchall()

        print('-' * 60)
        print('-- Datos de la consulta')
        print('-' * 60)
        for row in result:
            print(row)
        print('-' * 60)

    except Exception as e:
        print("Error al conectarse a la base de datos MySQL:", str(e))
        session.rollback()

local_filename = "order_extract.csv"
with open(local_filename, 'w', newline='') as fp:
    csv_w = csv.writer(fp, delimiter='|')
    csv_w.writerows(result)

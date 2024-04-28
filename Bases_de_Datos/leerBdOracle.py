from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import configparser
import csv

parser = configparser.ConfigParser()
parser.read("conexiones.conf")
hostname = parser.get("oracle_config", "hostname")
port = parser.get("oracle_config", "port")
username = parser.get("oracle_config", "username")
service_name = parser.get("oracle_config", "service_name")
password = parser.get("oracle_config", "password")

database_url = f"oracle+cx_oracle://{username}:{password}@{hostname}:{port}/?service_name={service_name}"

engine = create_engine(database_url)

Session = sessionmaker(bind=engine)

with Session() as session:
    try:
        session.execute(text('SELECT 1 FROM DUAL'))
        print("Conexión Oracle establecida!")

        query = text("SELECT * FROM ORDERS")

        result = session.execute(query).fetchall()

        print('-' * 60)
        print('-- Datos de la consulta')
        print('-' * 60)

        for row in result:
            print(row)

        print('-' * 60)

    except Exception as e:
        print("Error al conectarse a la base de datos Oracle:", str(e))
        session.rollback()

local_filename = "order_extract.csv"
with open(local_filename, 'w', newline='') as fp:
    csv_w = csv.writer(fp, delimiter='|')
    csv_w.writerows(result)
    
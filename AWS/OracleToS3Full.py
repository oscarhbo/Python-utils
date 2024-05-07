from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import configparser
import csv
import boto3


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


print('-' * 60)
print('-- Inicia escritura de archivo en Local')
print('-' * 60)


local_filename = "order_extract.csv"
with open(local_filename, 'w', newline='') as fp:
    csv_w = csv.writer(fp, delimiter='|')
    csv_w.writerows(result)


print('-' * 60)
print('-- Inicia transferencia de archivo en S3')
print('-' * 60)


local_filename = "order_extract.csv"

""" parser = configparser.ConfigParser()
parser.read("conexiones.conf") """
access_key = parser.get("aws_boto_cred", "access_key")
secret_key = parser.get("aws_boto_cred", "secret_key")
bucket_name = parser.get("aws_boto_cred", "bucket_name")

s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

s3_file = local_filename

s3.upload_file(local_filename, bucket_name, s3_file)

print('-' * 60)
print(f'-- archivo {local_filename} cargado correctamente a S3.')
print('-' * 60)
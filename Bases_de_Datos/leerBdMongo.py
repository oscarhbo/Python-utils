import pymongo
import configparser
import csv

parser = configparser.ConfigParser()
parser.read("conexiones.conf")
hostname = parser.get("mongodb_config", "hostname")
port = parser.get("mongodb_config", "port")
username = parser.get("mongodb_config", "username")
dbname = parser.get("mongodb_config", "database")
password = parser.get("mongodb_config", "password")

#uri = f"mongodb://{username}:{password}@{hostname}:{port}/{dbname}"
uri = f"mongodb://{username}:{password}@{hostname}:{port}/{dbname}?authSource=admin"

client = pymongo.MongoClient(uri)
db = client[dbname]

collection = db['Orders']


try:
    documents = list(collection.find())
    
    print('-' * 60)
    print('-- Datos de la consulta')
    print('-' * 60)
    for doc in documents:
        print(doc)
    print('-' * 60)

except Exception as e:
    print("Error al conectarse a la base de datos MongoDB:", str(e))

local_filename = "order_extract.csv"
with open(local_filename, 'w', newline='') as fp:
    csv_w = csv.writer(fp, delimiter='|')
    for doc in documents:
        csv_w.writerow([doc.get(field) for field in ['_id', 'item', 'quantity', 'price']]) 

client.close()

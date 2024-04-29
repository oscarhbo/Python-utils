from pymongo import MongoClient
import configparser

parser = configparser.ConfigParser()
parser.read("conexiones.conf")
hostname = parser.get("mongodb_config", "hostname")
port = parser.get("mongodb_config", "port")
username = parser.get("mongodb_config", "username")
dbname = parser.get("mongodb_config", "database")
password = parser.get("mongodb_config", "password")

#uri = f"mongodb://{username}:{password}@{hostname}:{port}/?authSource=admin"
#uri = f"mongodb://{username}:{password}@{hostname}:{port}/{dbname}"
uri = f"mongodb://{username}:{password}@{hostname}:{port}/{dbname}?authSource=admin"

client = MongoClient(uri)
db = client[dbname]

collection = db['Orders']

documents = [
    {"item": "Agenda", "quantity": 10, "price": 150.0},
    {"item": "escritorio", "quantity": 50, "price": 3605.75},
    {"item": "Cuaderno", "quantity": 20, "price": 45.0}
]

result = collection.insert_many(documents)

print(f"Documentos insertados: {result.inserted_ids}")

client.close()

import boto3
import configparser


print('-' * 60)
print('-- Inicia escritura de archivo en S3')
print('-' * 60)


local_filename = "order_extract.csv"

parser = configparser.ConfigParser()
parser.read("conexiones.conf")
access_key = parser.get("aws_boto_cred", "access_key")
secret_key = parser.get("aws_boto_cred", "secret_key")
bucket_name = parser.get("aws_boto_cred", "bucket_name")

s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

s3_file = local_filename

s3.upload_file(local_filename, bucket_name, s3_file)

print('-' * 60)
print(f'-- archivo {local_filename} cargado correctamente a S3.')
print('-' * 60)
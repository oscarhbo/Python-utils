import configparser
import os

def cargar_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config

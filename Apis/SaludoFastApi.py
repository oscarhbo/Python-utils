from fastapi import FastAPI

app = FastAPI()

@app.get("/saludo/{nombre}")
def saludar(nombre: str):
    return {"mensaje": f"Que tal {nombre}, este saludo vien desde una API con FastAPI"}
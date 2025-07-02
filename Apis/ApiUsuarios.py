from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Crear instancia de FastAPI
app = FastAPI()

# Conexión a base de datos SQLite
DATABASE_URL = "sqlite:///./usuarios.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Modelo SQLAlchemy (Base de datos)
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# Crear la tabla
Base.metadata.create_all(bind=engine)

# Modelo Pydantic para entrada/salida de datos
class UsuarioCreate(BaseModel):
    nombre: str
    email: str

class UsuarioOut(UsuarioCreate):
    id: int

# Dependencia para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear usuario
@app.post("/usuarios/", response_model=UsuarioOut)
def crear_usuario(usuario: UsuarioCreate):
    db = next(get_db())
    db_usuario = Usuario(nombre=usuario.nombre, email=usuario.email)
    db.add(db_usuario)
    try:
        db.commit()
        db.refresh(db_usuario)
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return db_usuario

# Obtener todos los usuarios
@app.get("/usuarios/", response_model=List[UsuarioOut])
def leer_usuarios():
    db = next(get_db())
    return db.query(Usuario).all()

# Obtener un usuario por ID
@app.get("/usuarios/{id}", response_model=UsuarioOut)
def leer_usuario(id: int):
    db = next(get_db())
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

# Actualizar un usuario
@app.put("/usuarios/{id}", response_model=UsuarioOut)
def actualizar_usuario(id: int, datos: UsuarioCreate):
    db = next(get_db())
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.nombre = datos.nombre
    usuario.email = datos.email
    db.commit()
    return usuario

# Eliminar usuario
@app.delete("/usuarios/{id}")
def eliminar_usuario(id: int):
    db = next(get_db())
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": f"Usuario con ID {id} eliminado"}

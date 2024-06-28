import pandas as pd
import numpy as np

def crear_df_dummy(size = 10_000):

  df = pd.DataFrame()
  df['edad'] = np.random.randint(10, 100, size)
  df['sexo'] = np.random.choice(['FEMENINO', 'MASCULINO'], size)
  df['horas_trabajo'] = np.random.randint(4, 10, size)
  df['pct_efectividad'] = np.random.rand(size)
  df['premio'] = np.random.choice(['Viernes Feliz', 'Día Libre', 'Bono'], size)
  df['castigo'] = np.random.choice(['Trabajo Sábado', 'Oficina', 'Más horas Trabajo'], size)

  return df

print("Inicia Generación de DataFrame")

df = crear_df_dummy()

df['recompensa'] = df['castigo']

df.loc [(df['edad'] >=90) | ((df['horas_trabajo'] >= 5) & (df['pct_efectividad'] >= 0.7)), 'recompensa'] = df['premio']

print(df.head())

print("Termina Generación de DataFrame")
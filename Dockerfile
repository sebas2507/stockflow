# Imagen base: Python oficial en su versión "slim" (más liviana)
FROM python:3.14-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /code

# 1) Primero solo las dependencias: esta capa queda en caché
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Después el código: si solo cambias código, no se reinstala nada
COPY app ./app

EXPOSE 8000

# Al arrancar: crea las tablas y los datos iniciales (idempotente) y levanta la API
CMD ["sh", "-c", "python -m app.seed && fastapi run app/main.py --port 8000"]
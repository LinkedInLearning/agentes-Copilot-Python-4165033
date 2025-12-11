# Imagen base con Python 3.12
FROM python:3.12-slim

# No .pyc y logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copiamos los archivos de dependencias de uv
COPY pyproject.toml uv.lock ./

# Instalamos uv (gestor de deps)
RUN pip install --no-cache-dir uv

# Instalamos dependencias según el lockfile (sin las de dev)
RUN uv sync --frozen --no-dev

# Copiamos el resto del código (incluye main.py)
COPY . .

# Exponemos el puerto interno
EXPOSE 8000

# Arrancamos la API FastAPI en 0.0.0.0:8000
# OJO: aquí usamos main:app (tu fichero + tu objeto FastAPI)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

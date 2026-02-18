FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el backend
COPY backend/ /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


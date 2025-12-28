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
#requirements.txt esta en la raiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el backend
COPY backend/ /app/

# Por defecto: arranca la API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

